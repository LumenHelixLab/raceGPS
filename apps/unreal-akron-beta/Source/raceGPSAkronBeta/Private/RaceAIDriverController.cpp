#include "RaceAIDriverController.h"
#include "RaceContactPolicy.h"
#include "RaceAIBehaviorPolicy.h"
#include "EngineUtils.h"
#include "Components/SkeletalMeshComponent.h"
#include "ClevelandModuleCompat.h"
#include "RacingLineComponent.h"
#include "RaceGridManager.h"
#include "Misc/CommandLine.h"

namespace
{
RaceAIBehaviorPolicy::Vector PolicyVector(const FVector& V)
{
    return {V.X, V.Y, V.Z};
}

RaceAIBehaviorPolicy::Box VehicleBounds(const USkeletalMeshComponent* Mesh)
{
    const auto Local = Mesh->CalcBounds(FTransform::Identity);
    const FTransform& World = Mesh->GetComponentTransform();
    return {PolicyVector(World.TransformPosition(Local.Origin)),
        PolicyVector(World.TransformVector(FVector(Local.BoxExtent.X, 0, 0))),
        PolicyVector(World.TransformVector(FVector(0, Local.BoxExtent.Y, 0))),
        PolicyVector(World.TransformVector(FVector(0, 0, Local.BoxExtent.Z)))};
}
}

ARaceAIDriverController::ARaceAIDriverController()
{
	bWantsPlayerState = false;
	PrimaryActorTick.bCanEverTick = true;
	Personality = FRaceAIPersonality::ConservativeAI01();
}

void ARaceAIDriverController::ConfigureDriver(URacingLineComponent* InLine, URaceSessionManager* InSession, int32 InSlot, const FRaceAIPersonality& InPersonality)
{
	RacingLine = InLine;
	SessionManager = InSession;
	SlotIndex = InSlot;
	Personality = InPersonality;
	NoiseSeed = 17 + InSlot * 91;
	LapIndex = 0;
	bFinished = false;
	bHavePrevS = false;
	bLeftStartZone = false;
	LiveElapsed = 0.f;
	PeakSpeedKmh = 0.f;
	StuckTimer = 0.f;
	OverturnedTimer = 0.f;
	RecoveryTimer = 0.f;
	RecoveryAnchorS = 0.f;
	RecoveryStartLocation = FVector::ZeroVector;
	CurrentSplineDistance = 0.f;
	TargetSplineDistance = 0.f;
	LastLapTimeSec = 0.f;
	RecoveryState = ERaceRecoveryState::None;
	bLoggedSkipRecovery = false;
	ApplyRecoveryModeFromFlags();
}

void ARaceAIDriverController::SetGridManager(ARaceGridManager* InGrid)
{
	GridManager = InGrid;
}

void ARaceAIDriverController::ApplyRecoveryModeFromFlags()
{
	const TCHAR* Cmd = FCommandLine::Get();
	bAggressiveRecovery = FParse::Param(Cmd, TEXT("ClevelandAutoLap"))
		|| FParse::Param(Cmd, TEXT("ClevelandPlaytest"));
	if (bAggressiveRecovery)
	{
		// Diagnostic timing may differ, but safe recovery never advances the car.
		UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: AI slot=%d aggressive recovery (AutoLap/playtest)"), SlotIndex);
		return;
	}
	// Human race: settle contact, try reversing, then safely reset a failed rejoin.
	Gains.RecoveryStuckDelaySec = 3.0f;
	Gains.RecoveryMaxCteCm = 1800.f;
	Gains.RecoverySteerBrakeSec = 1.2f;
	Gains.RecoveryReverseSec = 1.0f;
	UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: AI slot=%d soft recovery (occupied-space check, no forward gain)"), SlotIndex);
}

void ARaceAIDriverController::OnPossess(APawn* InPawn)
{
	Super::OnPossess(InPawn);
	LapStartWorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.f;
}

bool ARaceAIDriverController::IsRaceLive() const
{
	return RaceGPS_IsSessionRacing(SessionManager);
}

float ARaceAIDriverController::GetRaceProgress() const
{
	const float Length = (RacingLine && RacingLine->IsValidLine()) ? RacingLine->TrackLength : 0.f;
	return RaceAIControlMath::RaceProgress(LapIndex, Length, CurrentSplineDistance);
}

void ARaceAIDriverController::ZeroVehicleInputs(AChaosVehiclePawn* Vehicle)
{
	if (!Vehicle)
	{
		return;
	}
	Vehicle->SetDriveOverride(0.f, 0.f, 1.f, true);
	ThrottleCommand = 0.f;
	BrakeCommand = 1.f;
	SteeringCommand = 0.f;
	PublishTelemetry();
}

void ARaceAIDriverController::ApplyCommands(AChaosVehiclePawn* Vehicle, float Steer, float Throttle, float Brake, bool bHandbrake)
{
	if (!Vehicle)
	{
		return;
	}
    double NearestGapM = -1.0;
    double LeaderKmh = 0.0;
    const bool bReversing = Throttle < 0.f;
    const FVector Direction = Vehicle->GetActorForwardVector().GetSafeNormal2D() * (bReversing ? -1.f : 1.f);
    if (Vehicle->GetMesh() && GetWorld())
    {
        const auto OwnBounds = VehicleBounds(Vehicle->GetMesh());
        for (TActorIterator<AChaosVehiclePawn> It(GetWorld()); It; ++It)
        {
            AChaosVehiclePawn* Other = *It;
            if (Other == Vehicle || !Other->GetMesh()) continue;
            const double Gap = RaceAIBehaviorPolicy::BumperGapMetres(OwnBounds,
                VehicleBounds(Other->GetMesh()), PolicyVector(Direction));
            if (Gap >= 0.0 && (NearestGapM < 0.0 || Gap < NearestGapM))
            {
                NearestGapM = Gap;
                LeaderKmh = FMath::Max(0.0, FVector::DotProduct(Other->GetVelocity(), Direction) * 0.036);
            }
        }
    }
    if (NearestGapM >= 0.0)
    {
        const auto Safe = RaceContactPolicy::Drive(260.0, Vehicle->GetSpeedKmh(), NearestGapM, LeaderKmh);
        Throttle = (bReversing ? -1.f : 1.f) * FMath::Min(FMath::Abs(Throttle), float(Safe.throttle));
        Brake = FMath::Max(Brake, float(Safe.brake));
        if (Safe.targetKmh < 5.0 && RecoveryState == ERaceRecoveryState::None) StuckTimer = 0.f;
    }
    ThrottleCommand = Throttle;
    BrakeCommand = Brake;
    SteeringCommand = Steer;
    Vehicle->SetDriveOverride(Steer, Throttle, Brake, bHandbrake);
}

void ARaceAIDriverController::PublishTelemetry()
{
	Telemetry.CurrentSplineDistance = CurrentSplineDistance;
	Telemetry.TargetSplineDistance = TargetSplineDistance;
	Telemetry.CrossTrackError = CrossTrackError;
	Telemetry.HeadingError = HeadingError;
	Telemetry.CurrentSpeed = CurrentSpeed;
	Telemetry.TargetSpeed = TargetSpeed;
	Telemetry.ThrottleCommand = ThrottleCommand;
	Telemetry.BrakeCommand = BrakeCommand;
	Telemetry.SteeringCommand = SteeringCommand;
	Telemetry.RecoveryState = RecoveryState;
	Telemetry.LapProgress = LapProgress;
}

void ARaceAIDriverController::DetectLapWrap(float NewS, float TrackLength)
{
	if (TrackLength <= KINDA_SMALL_NUMBER)
	{
		return;
	}
	if (!bHavePrevS)
	{
		PrevS = NewS;
		bHavePrevS = true;
		return;
	}
	if (NewS > 0.15f * TrackLength && NewS < 0.90f * TrackLength)
	{
		bLeftStartZone = true;
	}
	const bool bWrapped =
		bLeftStartZone &&
		(PrevS > 0.80f * TrackLength) &&
		(NewS < 0.20f * TrackLength);
	if (bWrapped)
	{
		const float Now = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.f;
		LastLapTimeSec = Now - LapStartWorldTime;
		LapStartWorldTime = Now;
		LapIndex += 1;
		if (GridManager)
		{
			GridManager->NotifyVehicleLapComplete(SlotIndex, LastLapTimeSec);
		}
		if (LapIndex >= 1)
		{
			bFinished = true;
		}
	}
	PrevS = NewS;
}

void ARaceAIDriverController::SnapToNearestSpline(AChaosVehiclePawn* Vehicle)
{
	if (!Vehicle || !RacingLine || !RacingLine->IsValidLine())
	{
		return;
	}
    // Same location along the course in both play and diagnostic modes; never +25m.
    // Recovery uses physical stationing, including a car behind the start line.
    // The early-race steering normalization to zero must not move that car ahead.
    const float PhysicalS = RacingLine->GetNearestS(Vehicle->GetActorLocation());
    const float S = float(RaceAIBehaviorPolicy::RecoveryStation(RecoveryAnchorS,
        PhysicalS, RacingLine->TrackLength));
    const float Lat = RaceAIControlMath::LateralOffsetCm(Personality.Aggression, Gains.MaxLateralOffsetCm);
    FTransform Pose = RacingLine->GetPoseAtS(S, Lat);
    Pose.AddToTranslation(FVector(0.f, 0.f, 50.f));
    if (!Vehicle->TryRecoverAtPose(Pose))
    {
        ApplyCommands(Vehicle, 0.f, 0.f, 1.f, true);
        return; // wait for space; do not teleport through the other car
    }
    CurrentSplineDistance = S;
    PrevS = S;
    bHavePrevS = false; // teleport must not be interpreted as crossing the lap boundary
    if (GridManager) GridManager->NotifyVehicleRecovered(SlotIndex, S);
    RecoveryState = ERaceRecoveryState::None;
    RecoveryTimer = 0.f;
    StuckTimer = 0.f;
    OverturnedTimer = 0.f;
    ApplyCommands(Vehicle, 0.f, 0.f, 1.f, false);
    UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: safe recovery slot=%d s=%.1f"), SlotIndex, S);
}

void ARaceAIDriverController::TickRecovery(AChaosVehiclePawn* Vehicle, float DeltaSeconds, float AbsCteCm)
{
	if (!Vehicle)
	{
		return;
	}

	const bool bTriggered = OverturnedTimer > Gains.RecoveryStuckDelaySec || RaceAIControlMath::RecoveryTrigger(
		CurrentSpeed,
		ThrottleCommand,
		StuckTimer,
		AbsCteCm,
		Gains.RecoverySpeedKmh,
		Gains.RecoveryThrottleThresh,
		Gains.RecoveryStuckDelaySec,
		Gains.RecoveryMaxCteCm);

	if (RecoveryState == ERaceRecoveryState::None && bTriggered)
	{
		RecoveryState = ERaceRecoveryState::SteerBrake;
		RecoveryTimer = 0.f;
		RecoveryAnchorS = RacingLine->GetNearestS(Vehicle->GetActorLocation());
		RecoveryStartLocation = Vehicle->GetActorLocation();
	}

	if (RecoveryState == ERaceRecoveryState::None)
	{
		return;
	}

	RecoveryTimer += DeltaSeconds;
	const FVector Tangent = RacingLine ? RacingLine->GetTangentAtS(CurrentSplineDistance) : Vehicle->GetActorForwardVector();
	HeadingError = RaceAIControlMath::SignedHeadingErrorRad(Vehicle->GetActorForwardVector(), Tangent);
	const float CteM = CrossTrackError * 0.01f;
	SteeringCommand = RaceAIControlMath::SteeringCommand(HeadingError, CteM, Gains.KHeading, Gains.KCrossTrack);

	if (RecoveryState == ERaceRecoveryState::SteerBrake)
	{
		// Settle after contact before trying to rejoin.
		ApplyCommands(Vehicle, SteeringCommand, 0.f, 0.6f, false);
		if (RecoveryTimer >= Gains.RecoverySteerBrakeSec)
		{
			RecoveryState = ERaceRecoveryState::Reverse;
			RecoveryTimer = 0.f;
			RecoveryStartLocation = Vehicle->GetActorLocation();
		}
		return;
	}

	if (RecoveryState == ERaceRecoveryState::Reverse)
	{
		// Steering reverses with travel direction; the pawn selects an actual reverse gear.
		// ApplyCommands senses behind the car and refuses to back into an occupied gap.
		ApplyCommands(Vehicle, -SteeringCommand, -0.25f, 0.f, false);
		if (RecoveryTimer >= Gains.RecoveryReverseSec)
		{
			RecoveryState = ERaceRecoveryState::ResetSnap;
			RecoveryTimer = 0.f;
		}
		return;
	}

	if (RecoveryState == ERaceRecoveryState::ResetSnap)
	{
		const float MovedCm = FVector::Dist2D(RecoveryStartLocation, Vehicle->GetActorLocation());
		if (RaceAIBehaviorPolicy::ShouldResetAfterAttempt(Vehicle->GetActorUpVector().Z,
			AbsCteCm, Gains.RecoveryMaxCteCm, MovedCm))
		{
			// An overturned or trapped car can need a reset even right on the racing line.
			SnapToNearestSpline(Vehicle);
		}
		else
		{
			RecoveryState = ERaceRecoveryState::None;
			RecoveryTimer = 0.f;
			StuckTimer = 0.f;
			OverturnedTimer = 0.f;
			ApplyCommands(Vehicle, 0.f, 0.f, 0.6f, false);
		}
	}
}

void ARaceAIDriverController::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	TickDriveForPawn(Cast<AChaosVehiclePawn>(GetPawn()), DeltaSeconds);
}

void ARaceAIDriverController::TickDriveForPawn(AChaosVehiclePawn* Vehicle, float DeltaSeconds)
{
	if (!Vehicle || !RacingLine || !RacingLine->IsValidLine())
	{
		return;
	}

	CurrentSpeed = Vehicle->GetSpeedKmh();
	float CteCm = 0.f;
	CurrentSplineDistance = RacingLine->GetNearestSWithCte(Vehicle->GetActorLocation(), CteCm);
	const float Length = RacingLine->TrackLength;
	// Start==finish nearest-S: sitting on the grid reports s~TrackLength. Treat as 0 until we have raced.
	if (LapIndex == 0 && LiveElapsed < 20.f && Length > KINDA_SMALL_NUMBER && CurrentSplineDistance > 0.85f * Length)
	{
		CurrentSplineDistance = 0.f;
		CteCm = 0.f;
	}
	CrossTrackError = CteCm;
	LapProgress = (Length > KINDA_SMALL_NUMBER)
		? (CurrentSplineDistance / Length)
		: 0.f;

	if (GridManager)
	{
		LapIndex = GridManager->GetCompletedLaps(SlotIndex);
		bFinished = GridManager->HasVehicleFinished(SlotIndex);
	}
	if (!IsRaceLive() || bFinished)
	{
		LiveElapsed = 0.f;
		ZeroVehicleInputs(Vehicle);
		return;
	}
	if (LiveElapsed == 0.f)
	{
		LapStartWorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.f;
	}
	if (!GridManager) DetectLapWrap(CurrentSplineDistance, Length);
	LiveElapsed += DeltaSeconds;
	PeakSpeedKmh = FMath::Max(PeakSpeedKmh, CurrentSpeed);
	if (CurrentSpeed < 0.5f && LiveElapsed < 8.f)
	{
		Vehicle->WakeForDrive();
	}

	if (CurrentSpeed < Gains.RecoverySpeedKmh && ThrottleCommand > Gains.RecoveryThrottleThresh)
	{
		StuckTimer += DeltaSeconds;
	}
	else
	{
		StuckTimer = 0.f;
	}
	if (CurrentSpeed < Gains.RecoverySpeedKmh && Vehicle->GetActorUpVector().Z < 0.35f)
	{
		OverturnedTimer += DeltaSeconds;
	}
	else
	{
		OverturnedTimer = 0.f;
	}

	// Do not reverse-recover a car that has never actually rolled. On a crawl
	// (speed~0) reverse every ~8s undoes the few centimeters of progress.
	// But a car that crawls forever never reaches CPs and blocks EndRace, so a
	// never-rolled car still gets recovery after a much longer stuck window.
	const bool bEverRolled = PeakSpeedKmh >= Gains.RecoverySpeedKmh;
	const bool bLongStuck = StuckTimer > 4.f * Gains.RecoveryStuckDelaySec;
	const bool bOverturned = OverturnedTimer > Gains.RecoveryStuckDelaySec;
	if (!bEverRolled && !bLongStuck && !bOverturned && RecoveryState == ERaceRecoveryState::None)
	{
		if (LiveElapsed > 8.f && !bLoggedSkipRecovery)
		{
			bLoggedSkipRecovery = true;
			UE_LOG(LogTemp, Warning,
				TEXT("raceGPS Cleveland: skip stuck recovery slot=%d peak=%.2f km/h (need >= %.1f) - reverse would fight crawl"),
				SlotIndex, PeakSpeedKmh, Gains.RecoverySpeedKmh);
		}
	}
	const bool bAllowRecovery = LiveElapsed > 8.f &&
		(bEverRolled || bLongStuck || bOverturned || RecoveryState != ERaceRecoveryState::None);
	if (bAllowRecovery && (RecoveryState != ERaceRecoveryState::None
		|| bOverturned || RaceAIControlMath::RecoveryTrigger(
			CurrentSpeed, ThrottleCommand, StuckTimer, FMath::Abs(CteCm),
			Gains.RecoverySpeedKmh, Gains.RecoveryThrottleThresh,
			Gains.RecoveryStuckDelaySec, Gains.RecoveryMaxCteCm)))
	{
		TickRecovery(Vehicle, DeltaSeconds, FMath::Abs(CteCm));
		PublishTelemetry();
		return;
	}

	const float LookAheadCm = (Gains.LookAheadMeters + Gains.LookAheadSpeedGain * CurrentSpeed) * 100.f;
	TargetSplineDistance = RaceAIControlMath::WrapS(CurrentSplineDistance + LookAheadCm, RacingLine->TrackLength);

	const float Lateral = RaceAIControlMath::LateralOffsetCm(Personality.Aggression, Gains.MaxLateralOffsetCm);
	const FVector TargetPos = RacingLine->GetPoseAtS(TargetSplineDistance, Lateral).GetLocation();
	const FVector Dir = TargetPos - Vehicle->GetActorLocation();
	HeadingError = RaceAIControlMath::SignedHeadingErrorRad(Vehicle->GetActorForwardVector(), Dir);

	const float CteMeters = CteCm * 0.01f;
	const float WorldTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.f;
	const float Noise = Personality.ReactionNoise * FMath::Sin((WorldTime * 7.31f) + static_cast<float>(NoiseSeed));
	SteeringCommand = RaceAIControlMath::SteeringCommand(
		HeadingError + Noise * 0.15f,
		CteMeters,
		Gains.KHeading * (0.75f + 0.25f * Personality.Skill),
		Gains.KCrossTrack);

	const float Kappa = RacingLine->GetCurvatureAtS(TargetSplineDistance);
	const float Vmax = Gains.VmaxKmh * (0.85f + 0.15f * Personality.Skill);
	const float Vmin = Gains.VminKmh * Personality.CornerSpeed;
	TargetSpeed = RaceAIControlMath::TargetSpeedKmh(FMath::Abs(Kappa), Vmax, Vmin, Gains.KCurve);

    // The same target-speed law drives the physical rival and diagnostic auto-driver.
    // Sense bumper clearance, not just racing-line progress, so contact causes a response.
    const auto Drive = RaceContactPolicy::Drive(TargetSpeed, CurrentSpeed, -1.0, 0.0);
    ThrottleCommand = float(Drive.throttle);
    BrakeCommand = float(Drive.brake);

	ApplyCommands(Vehicle, SteeringCommand, ThrottleCommand, BrakeCommand, false);
	PublishTelemetry();
}
