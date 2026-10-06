#include "RaceAIDriverController.h"
#include "RaceContactPolicy.h"
#include "EngineUtils.h"
#include "Components/SkeletalMeshComponent.h"
#include "ClevelandModuleCompat.h"
#include "RacingLineComponent.h"
#include "RaceGridManager.h"
#include "Misc/CommandLine.h"

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
	RecoveryTimer = 0.f;
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
	// Human race: slower trigger, wider CTE tolerance, no punch-to-teleport cadence.
	Gains.RecoveryStuckDelaySec = 3.0f;
	Gains.RecoveryMaxCteCm = 1800.f;
	Gains.RecoverySteerBrakeSec = 1.2f;
	Gains.RecoveryReverseSec = 1.0f;
	UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: AI slot=%d soft recovery (human race, no aggressive teleport)"), SlotIndex);
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
	BrakeCommand = 0.f;
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
    const FVector Forward = Vehicle->GetActorForwardVector().GetSafeNormal2D();
    const FVector Right(-Forward.Y, Forward.X, 0.f);
    const auto OwnBounds = Vehicle->GetMesh()->Bounds;
    for (TActorIterator<AChaosVehiclePawn> It(GetWorld()); It; ++It)
    {
        AChaosVehiclePawn* Other = *It;
        if (Other == Vehicle || !Other->GetMesh()) continue;
        const auto OtherBounds = Other->GetMesh()->Bounds;
        const FVector Delta = OtherBounds.Origin - OwnBounds.Origin;
        const double Ahead = FVector::DotProduct(Delta, Forward);
        if (Ahead <= 0.0 || FMath::Abs(Delta.Z) > OwnBounds.BoxExtent.Z + OtherBounds.BoxExtent.Z) continue;
        const FVector SumExtent = OwnBounds.BoxExtent + OtherBounds.BoxExtent;
        const double LateralLimit = FMath::Abs(Right.X) * SumExtent.X + FMath::Abs(Right.Y) * SumExtent.Y + 50.0;
        if (FMath::Abs(FVector::DotProduct(Delta, Right)) > LateralLimit) continue;
        const double HalfLengths = FMath::Abs(Forward.X) * SumExtent.X + FMath::Abs(Forward.Y) * SumExtent.Y;
        const double Gap = FMath::Max(0.0, Ahead - HalfLengths) * 0.01;
        if (NearestGapM < 0.0 || Gap < NearestGapM)
        {
            NearestGapM = Gap;
            LeaderKmh = FMath::Max(0.0, FVector::DotProduct(Other->GetVelocity(), Forward) * 0.036);
        }
    }
    if (NearestGapM >= 0.0)
    {
        const auto Safe = RaceContactPolicy::Drive(260.0, Vehicle->GetSpeedKmh(), NearestGapM, LeaderKmh);
        Throttle = FMath::Min(Throttle, float(Safe.throttle));
        Brake = FMath::Max(Brake, float(Safe.brake));
        if (Safe.targetKmh < 5.0) StuckTimer = 0.f;
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
    const float S = bHavePrevS ? PrevS : RacingLine->GetNearestS(Vehicle->GetActorLocation());
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
    RecoveryState = ERaceRecoveryState::None;
    RecoveryTimer = 0.f;
    StuckTimer = 0.f;
    UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: safe recovery slot=%d s=%.1f"), SlotIndex, S);
}

void ARaceAIDriverController::TickRecovery(AChaosVehiclePawn* Vehicle, float DeltaSeconds, float AbsCteCm)
{
	if (!Vehicle)
	{
		return;
	}

	const bool bTriggered = RaceAIControlMath::RecoveryTrigger(
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
		}
		return;
	}

	if (RecoveryState == ERaceRecoveryState::Reverse)
	{
		// Legacy Reverse state now makes a gentle forward rejoin, bounded by rival clearance.
		ApplyCommands(Vehicle, SteeringCommand, 0.25f, 0.f, false);
		if (RecoveryTimer >= Gains.RecoveryReverseSec)
		{
			RecoveryState = ERaceRecoveryState::ResetSnap;
			RecoveryTimer = 0.f;
		}
		return;
	}

	if (RecoveryState == ERaceRecoveryState::ResetSnap)
	{
		if (bAggressiveRecovery)
		{
			SnapToNearestSpline(Vehicle);
		}
		else if (AbsCteCm > Gains.RecoveryMaxCteCm)
		{
			// Human: teleport only when far offline; otherwise drop recovery and keep driving.
			SnapToNearestSpline(Vehicle);
		}
		else
		{
			RecoveryState = ERaceRecoveryState::None;
			RecoveryTimer = 0.f;
			StuckTimer = 0.f;
			UE_LOG(LogTemp, Verbose, TEXT("raceGPS Cleveland: skip soft teleport slot=%d cte=%.1f (human)"), SlotIndex, AbsCteCm);
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
	DetectLapWrap(CurrentSplineDistance, Length);
	LapProgress = (Length > KINDA_SMALL_NUMBER)
		? (CurrentSplineDistance / Length)
		: 0.f;

	if (!IsRaceLive() || bFinished)
	{
		LiveElapsed = 0.f;
		ZeroVehicleInputs(Vehicle);
		return;
	}
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

	// Do not reverse-recover a car that has never actually rolled. On a crawl
	// (speed~0) reverse every ~8s undoes the few centimeters of progress.
	// But a car that crawls forever never reaches CPs and blocks EndRace, so a
	// never-rolled car still gets recovery after a much longer stuck window.
	const bool bEverRolled = PeakSpeedKmh >= Gains.RecoverySpeedKmh;
	const bool bLongStuck = StuckTimer > 4.f * Gains.RecoveryStuckDelaySec;
	if (!bEverRolled && !bLongStuck)
	{
		if (RecoveryState != ERaceRecoveryState::None)
		{
			RecoveryState = ERaceRecoveryState::None;
			RecoveryTimer = 0.f;
		}
		if (LiveElapsed > 8.f && !bLoggedSkipRecovery)
		{
			bLoggedSkipRecovery = true;
			UE_LOG(LogTemp, Warning,
				TEXT("raceGPS Cleveland: skip stuck recovery slot=%d peak=%.2f km/h (need >= %.1f) - reverse would fight crawl"),
				SlotIndex, PeakSpeedKmh, Gains.RecoverySpeedKmh);
		}
	}
	const bool bAllowRecovery = LiveElapsed > 8.f && (bEverRolled || bLongStuck);
	if (bAllowRecovery && (RecoveryState != ERaceRecoveryState::None
		|| RaceAIControlMath::RecoveryTrigger(
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
