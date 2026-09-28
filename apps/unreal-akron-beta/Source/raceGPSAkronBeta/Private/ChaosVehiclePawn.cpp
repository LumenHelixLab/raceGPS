#include "ChaosVehiclePawn.h"
#include "RaceGPSVehicleWheels.h"
#include "ChaosWheeledVehicleMovementComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "Camera/CameraComponent.h"
#include "Components/InputComponent.h"
#include "Components/ArrowComponent.h"
#include "VehicleTuningData.h"
#include "VehicleAudioComponent.h"
#include "NeonHUD.h"
#include "Components/PointLightComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "CruiseSprintGameMode.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimInstance.h"
#include "PhysicsEngine/BodyInstance.h"

static EVehicleDifferential ToEngineDifferential(ERaceGPSDifferentialType Type)
{
    switch (Type)
    {
    case ERaceGPSDifferentialType::FrontWheelDrive: return EVehicleDifferential::FrontWheelDrive;
    case ERaceGPSDifferentialType::RearWheelDrive:  return EVehicleDifferential::RearWheelDrive;
    default:                                          return EVehicleDifferential::AllWheelDrive;
    }
}

AChaosVehiclePawn::AChaosVehiclePawn(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    PrimaryActorTick.bCanEverTick = true;
    // PrePhysics so pawn input writes land before Chaos MoveComp (DuringPhysics).
    // AssertMoveCompTickAfterPawn re-asserts PrePhysics ordering after recreates (no AddTickPrerequisite cycle).
    PrimaryActorTick.TickGroup = TG_PrePhysics;

    // Spring arm for chase camera
    SpringArm = CreateDefaultSubobject<USpringArmComponent>(TEXT("SpringArm"));
    SpringArm->SetupAttachment(GetMesh());
    SpringArm->TargetArmLength = 450.0f;
    SpringArm->bUsePawnControlRotation = false;
    SpringArm->bInheritPitch = false;
    SpringArm->bInheritRoll = false;
    SpringArm->bInheritYaw = true;
    SpringArm->SetRelativeRotation(FRotator(-10.0f, 0.0f, 0.0f));
    SpringArm->SocketOffset = FVector(0.0f, 0.0f, 120.0f);

    // Chase camera
    ChaseCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("ChaseCamera"));
    ChaseCamera->SetupAttachment(SpringArm, USpringArmComponent::SocketName);
    ChaseCamera->bUsePawnControlRotation = false;

    // Hood camera
    HoodCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("HoodCamera"));
    HoodCamera->SetupAttachment(GetMesh());
    HoodCamera->SetRelativeLocation(FVector(120.0f, 0.0f, 110.0f));
    HoodCamera->SetRelativeRotation(FRotator(0.0f, 0.0f, 0.0f));
    HoodCamera->bUsePawnControlRotation = false;
    HoodCamera->SetAutoActivate(false);

    // Arrow for forward direction
    Arrow = CreateDefaultSubobject<UArrowComponent>(TEXT("ForwardArrow"));
    Arrow->SetupAttachment(GetMesh());
    Arrow->SetRelativeLocation(FVector(180.0f, 0.0f, 50.0f));

    // Audio
    AudioComponent = CreateDefaultSubobject<UVehicleAudioComponent>(TEXT("AudioComponent"));

    // Default arcade steering curve (X = MPH, Y = fraction of max steer angle).
    // Full lock at parking speeds, gentle falloff to keep highway speed stable.
    FRichCurve* ArcadeCurve = ArcadeSteeringCurve.GetRichCurve();
    ArcadeCurve->Reset();
    ArcadeCurve->AddKey(0.0f, 1.0f);
    ArcadeCurve->AddKey(40.0f, 0.85f);
    ArcadeCurve->AddKey(80.0f, 0.6f);
    ArcadeCurve->AddKey(140.0f, 0.45f);

    static ConstructorHelpers::FObjectFinder<USkeletalMesh> VehicleMesh(
        TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SK_DodgeCharger2024.SK_DodgeCharger2024"));
    if (VehicleMesh.Succeeded() && GetMesh())
    {
        GetMesh()->SetSkeletalMesh(VehicleMesh.Object);
    }

    // Chaos CreateVehicle runs at movement-component registration during SpawnActor —
    // before PostInitializeComponents/BeginPlay — and disables mechanical sim when the
    // torque curve is empty. Inject the curve here so even the first create sees it.
    EnsureEngineDriveConfig();
}

void AChaosVehiclePawn::EnsureCarlaChargerMesh()
{
    if (!GetMesh())
    {
        return;
    }
    if (GetMesh()->GetSkeletalMeshAsset())
    {
        return;
    }
    if (USkeletalMesh* Loaded = LoadObject<USkeletalMesh>(nullptr,
        TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SK_DodgeCharger2024.SK_DodgeCharger2024")))
    {
        GetMesh()->SetSkeletalMesh(Loaded);
    }
}


void AChaosVehiclePawn::EnsureEngineDriveConfig()
{
    auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    if (!WheeledComp)
    {
        return;
    }
    // Chaos CreateVehicle disables mechanical sim when TorqueCurve is empty.
    // Must be filled BEFORE the first physics create (and kept filled across recreates).
    // ALWAYS inject a real torque curve. Clear ExternalCurve so Chaos reads our RichCurve keys
    // (BP may point at an empty UCurveFloat and still log "no torque curve" / disable mech).
    WheeledComp->EngineSetup.TorqueCurve.ExternalCurve = nullptr;
    FRichCurve* Curve = WheeledComp->EngineSetup.TorqueCurve.GetRichCurve();
    if (Curve)
    {
        Curve->Reset();
        // StraySpark-style torque curve (peak ~70% MaxRPM) — same as ApplyHellcatTune preset.
        Curve->AddKey(0.0f, 420.0f);
        Curve->AddKey(1500.0f, 620.0f);
        Curve->AddKey(3500.0f, 700.0f);
        Curve->AddKey(5000.0f, 680.0f);
        Curve->AddKey(6000.0f, 520.0f);
        Curve->AddKey(7000.0f, 380.0f);
    }
    WheeledComp->EngineSetup.MaxTorque = FMath::Max(WheeledComp->EngineSetup.MaxTorque, 700.0f);
    WheeledComp->EngineSetup.MaxRPM = FMath::Max(WheeledComp->EngineSetup.MaxRPM, 7000.0f);
    WheeledComp->EngineSetup.EngineBrakeEffect = 0.05f;
    if (WheeledComp->EngineSetup.EngineIdleRPM < 900.f)
    {
        WheeledComp->EngineSetup.EngineIdleRPM = 900.0f;
    }
    WheeledComp->TransmissionSetup.bUseAutomaticGears = true;
    WheeledComp->TransmissionSetup.ForwardGearRatios = { 3.5f, 2.1f, 1.4f, 1.0f, 0.8f };
    WheeledComp->TransmissionSetup.ReverseGearRatios = { 3.0f };
    WheeledComp->TransmissionSetup.FinalRatio = 4.0f;
    WheeledComp->TransmissionSetup.ChangeUpRPM = 5950.0f;
    WheeledComp->TransmissionSetup.ChangeDownRPM = 2800.0f;
    WheeledComp->TransmissionSetup.GearChangeTime = 0.15f;
    WheeledComp->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
    if (WheeledComp->DifferentialSetup.FrontRearSplit < 0.05f
        || WheeledComp->DifferentialSetup.FrontRearSplit > 0.95f)
    {
        WheeledComp->DifferentialSetup.FrontRearSplit = 0.5f;
    }
    // TorqueRatio: distinct Front/Rear CDOs with bAffectedByEngine before CreateVehicle.
    for (int32 i = 0; i < WheeledComp->WheelSetups.Num(); ++i)
    {
        FChaosWheelSetup& Setup = WheeledComp->WheelSetups[i];
        UClass* Wanted = (i < 2)
            ? URaceGPSVehicleWheelFront::StaticClass()
            : URaceGPSVehicleWheelRear::StaticClass();
        if (Setup.WheelClass != Wanted)
        {
            Setup.WheelClass = Wanted;
        }
    }
    WheeledComp->EnableMechanicalSim(true);
    WheeledComp->SetParked(false);
    WheeledComp->SetSleeping(false);
}

void AChaosVehiclePawn::AssertMoveCompTickAfterPawn()
{
    // Cycle-free: pawn TG_PrePhysics; NEVER AddTickPrerequisiteActor(this) (LogTick cycle).
    // Inputs are written in Tick before Super; MoveComp (DuringPhysics) reads them after.
    PrimaryActorTick.TickGroup = TG_PrePhysics;
    if (auto* MoveComp = GetVehicleMovementComponent())
    {
        MoveComp->PrimaryComponentTick.RemovePrerequisite(this, PrimaryActorTick);
        MoveComp->PrimaryComponentTick.TickGroup = TG_DuringPhysics;
        MoveComp->SetRequiresControllerForInputs(false);
    }
}

void AChaosVehiclePawn::PostInitializeComponents()
{
    EnsureEngineDriveConfig();
    Super::PostInitializeComponents();
    EnsureEngineDriveConfig();
}

void AChaosVehiclePawn::BeginPlay()
{
    // Torque curve MUST exist before Super::BeginPlay triggers Chaos CreateVehicle.
    EnsureEngineDriveConfig();
    Super::BeginPlay();
    InitChaosVehicleMovement();
    ApplyTuningData();

    // Arcade tire/handling config applies whether or not TuningData is set,
    // as long as the wheeled movement component and its WheelSetups exist.
    if (bEnableArcadeHandling)
    {
        if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent()))
        {
            ApplyArcadeHandling(WheeledComp);
        }
    }

    ApplyVehicleLook(VehicleLook);
    UpdateCameraView();

    if (auto* MoveComp = GetVehicleMovementComponent())
    {
        // Pawn Tick writes throttle before the Chaos component consumes it.
        AssertMoveCompTickAfterPawn();
        // ApplyHellcatTune sets RWD; with wrong AxleType that zeros TorqueRatio. Force AWD + curve.
        EnsureEngineDriveConfig();
        if (auto* WheeledEnable = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
        {
            WheeledEnable->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
            WheeledEnable->EnableMechanicalSim(true);
        }
        if (USkeletalMeshComponent* Skel = GetMesh())
        {
            Skel->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
            Skel->SetSimulatePhysics(true);
        }
        // Torque/mech already filled before Super; sticky Front/Rear classes (no per-frame recreate).
        EnsureEngineDriveConfig();
        EnsureDefaultWheels();
        EnsureEngineDriveConfig();
        // CRITICAL: first CreateVehicle may have cleared bMechanicalSimEnabled (empty BP curve)
        // without adding Engine to PVehicle. EnableMechanicalSim alone does NOT retrofit Engine —
        // must RecreatePhysicsState AFTER EnableMechanicalSim(true) + non-empty curve.
        EnsureEngineDriveConfig();
        if (auto* WheeledEnable2 = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
        {
            WheeledEnable2->EnableMechanicalSim(true);
            WheeledEnable2->RecreatePhysicsState();
            WheeledEnable2->EnableMechanicalSim(true);
            WheeledEnable2->SetTargetGear(1, true);
        }
        AssertMoveCompTickAfterPawn();
        MoveComp->SetParked(false);
        MoveComp->SetSleeping(false);
        if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
        {
            WheeledComp->SetTargetGear(1, true);
            UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: sim recreate class=%s sim=%d mech=%d curveEmpty=%d rpm=%.0f gear=%d tq=%.0f wheels=%d"),
                *GetNameSafe(GetClass()),
                (GetMesh() && GetMesh()->IsSimulatingPhysics()) ? 1 : 0,
                WheeledComp->bMechanicalSimEnabled ? 1 : 0,
                WheeledComp->EngineSetup.TorqueCurve.GetRichCurveConst()->IsEmpty() ? 1 : 0,
                WheeledComp->GetEngineRotationSpeed(),
                WheeledComp->GetCurrentGear(),
                WheeledComp->EngineSetup.MaxTorque,
                WheeledComp->Wheels.Num());
        }
        bChaosSimReady = true;
    }

    GetMesh()->OnComponentHit.AddDynamic(this, &AChaosVehiclePawn::OnVehicleHit);
}

void AChaosVehiclePawn::InitChaosVehicleMovement()
{
    auto* MoveComp = GetVehicleMovementComponent();
    if (!MoveComp) return;

    // Torque curve + EnableMechanicalSim MUST be set BEFORE any RecreatePhysicsState/EnsureDefaultWheels.
    EnsureEngineDriveConfig();

    if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
    {
        // Arcade Cleveland authoritative floor (fun street, not Hellcat sim).
        WheeledComp->EngineSetup.TorqueCurve.ExternalCurve = nullptr;
        WheeledComp->EngineSetup.MaxTorque = 700.0f;
        WheeledComp->EngineSetup.MaxRPM = 6500.0f;
        WheeledComp->EngineSetup.EngineIdleRPM = 1000.0f;
        WheeledComp->EngineSetup.EngineBrakeEffect = 0.0f;
        FRichCurve* Curve = WheeledComp->EngineSetup.TorqueCurve.GetRichCurve();
        Curve->Reset();
        Curve->AddKey(0.0f, 420.0f);
        Curve->AddKey(1500.0f, 620.0f);
        Curve->AddKey(3500.0f, 700.0f);
        Curve->AddKey(5000.0f, 680.0f);
        Curve->AddKey(6000.0f, 520.0f);
        Curve->AddKey(7000.0f, 380.0f);
        WheeledComp->EnableMechanicalSim(true);
        WheeledComp->TransmissionSetup.bUseAutomaticGears = true;
        WheeledComp->TransmissionSetup.ForwardGearRatios = { 4.5f, 2.8f, 1.9f, 1.35f, 1.0f };
        WheeledComp->TransmissionSetup.ReverseGearRatios = { 3.8f };
        WheeledComp->TransmissionSetup.FinalRatio = 4.2f;
        WheeledComp->TransmissionSetup.ChangeUpRPM = 5800.0f;
        WheeledComp->TransmissionSetup.ChangeDownRPM = 2200.0f;
        WheeledComp->TransmissionSetup.GearChangeTime = 0.12f;
        WheeledComp->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
        WheeledComp->EnableMechanicalSim(true);
        WheeledComp->SetParked(false);
        WheeledComp->SetSleeping(false);
        if (WheeledComp->GetCurrentGear() <= 0)
        {
            WheeledComp->SetTargetGear(1, true);
        }
        UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: engine MaxTorque=%.0f MaxRPM=%.0f gears=%d setups=%d wheels=%d curveEmpty=%d class=%s"),
            WheeledComp->EngineSetup.MaxTorque, WheeledComp->EngineSetup.MaxRPM,
            WheeledComp->TransmissionSetup.ForwardGearRatios.Num(),
            WheeledComp->WheelSetups.Num(), WheeledComp->Wheels.Num(),
            Curve->IsEmpty() ? 1 : 0,
            *GetNameSafe(GetClass()));
    }

    EnsureEngineDriveConfig();
    EnsureDefaultWheels();
    EnsureEngineDriveConfig();
    AssertMoveCompTickAfterPawn();
}

void AChaosVehiclePawn::SetTuningData(UVehicleTuningData* NewTuningData)
{
    if (!NewTuningData)
        return;

    TuningData = NewTuningData;
    ApplyTuningData();
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Tuning applied: %s"), *TuningData->DisplayName);
}

void AChaosVehiclePawn::ApplyTuningData()
{
    auto* MoveComp = GetVehicleMovementComponent();
    if (!MoveComp || !TuningData)
        return;

    // Vehicle mass and aero (base movement component)
    MoveComp->Mass = TuningData->VehicleMass;
    MoveComp->DragCoefficient = TuningData->DragCoefficient;
    MoveComp->ChassisWidth = TuningData->ChassisWidth;
    MoveComp->ChassisHeight = TuningData->ChassisHeight;
    MoveComp->DownforceCoefficient = TuningData->DownForceCoefficient;

    // Engine, transmission, differential and steering are on the wheeled movement component in UE 5.7
    auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp);
    if (!WheeledComp)
        return;

    // Engine
    WheeledComp->EngineSetup.MaxRPM = TuningData->MaxEngineRPM;
    WheeledComp->EngineSetup.EngineIdleRPM = TuningData->IdleRPM;
    WheeledComp->EngineSetup.EngineBrakeEffect = 0.0f; // BrakeTorque/10000 caused negative drvTq at thr=1
    WheeledComp->EngineSetup.MaxTorque = 700.0f; // arcade Cleveland floor

    // Steering
    WheeledComp->SteeringSetup.SteeringType = ESteeringType::Ackermann;

    // Transmission
    WheeledComp->TransmissionSetup.FinalRatio = TuningData->Transmission.FinalDriveRatio;
    WheeledComp->TransmissionSetup.ForwardGearRatios = TuningData->Transmission.GearRatios;
    WheeledComp->TransmissionSetup.ReverseGearRatios.Empty();
    WheeledComp->TransmissionSetup.ReverseGearRatios.Add(TuningData->Transmission.ReverseGearRatio);
    WheeledComp->TransmissionSetup.ChangeUpRPM = TuningData->Transmission.UpShiftRPM;
    WheeledComp->TransmissionSetup.ChangeDownRPM = TuningData->Transmission.DownShiftRPM;
    WheeledComp->TransmissionSetup.GearChangeTime = (TuningData->Transmission.ChangeUpTime + TuningData->Transmission.ChangeDownTime) * 0.5f;

    // Differential
    WheeledComp->DifferentialSetup.DifferentialType = ToEngineDifferential(TuningData->Differential.DifferentialType);
    WheeledComp->DifferentialSetup.FrontRearSplit = TuningData->Differential.FrontRearSplit;

    // Wheels
    for (int32 i = 0; i < TuningData->Wheels.Num() && i < WheeledComp->WheelSetups.Num(); ++i)
    {
        SetupWheel(WheeledComp, i, TuningData->Wheels[i]);
    }
}

void AChaosVehiclePawn::SetupWheel(UChaosWheeledVehicleMovementComponent* WheeledComp, int32 WheelIndex, const FWheelTuning& Wheel)
{
    if (!WheeledComp || WheelIndex >= WheeledComp->WheelSetups.Num())
        return;

    // In UE 5.7 wheel shape configuration lives on the UChaosVehicleWheel class default object.
    FChaosWheelSetup& Setup = WheeledComp->WheelSetups[WheelIndex];
    UClass* WheelClass = Setup.WheelClass ? static_cast<UClass*>(Setup.WheelClass) : UChaosVehicleWheel::StaticClass();
    UChaosVehicleWheel* WheelCDO = Cast<UChaosVehicleWheel>(WheelClass->GetDefaultObject(true));
    if (!WheelCDO)
    {
        return;
    }

    WheelCDO->WheelRadius = Wheel.Radius;
    WheelCDO->WheelWidth = Wheel.Width;
    WheelCDO->WheelMass = Wheel.Mass;
    WheelCDO->MaxSteerAngle = Wheel.SteerAngle;
    WheelCDO->bAffectedBySteering = Wheel.SteerAngle != 0.0f;
    WheelCDO->bAffectedByEngine = Wheel.bDrive;
    WheelCDO->bAffectedByHandbrake = Wheel.bHandbrake;

    // Suspension
    WheelCDO->SpringRate = Wheel.SuspensionStiffness;
    WheelCDO->SuspensionDampingRatio = Wheel.SuspensionDamping;
    WheelCDO->SuspensionMaxRaise = Wheel.MaxRaise;
    WheelCDO->SuspensionMaxDrop = Wheel.MaxDrop;
    WheelCDO->SuspensionForceOffset = FVector(0.0f, 0.0f, Wheel.SuspensionForceOffset);
}

void AChaosVehiclePawn::ApplyArcadeHandling(UChaosWheeledVehicleMovementComponent* WheeledComp)
{
    if (!WheeledComp)
        return;

    const int32 NumWheels = WheeledComp->WheelSetups.Num();
    if (NumWheels == 0)
        return;

    // Capture each wheel class's authored friction once, before any scaling, so
    // repeated calls (e.g. SetTuningData re-applying) never compound the multiplier.
    if (BaseWheelFriction.Num() != NumWheels)
    {
        BaseWheelFriction.SetNum(NumWheels);
        for (int32 i = 0; i < NumWheels; ++i)
        {
            UClass* WheelClass = WheeledComp->WheelSetups[i].WheelClass
                ? static_cast<UClass*>(WheeledComp->WheelSetups[i].WheelClass)
                : UChaosVehicleWheel::StaticClass();
            const UChaosVehicleWheel* WheelCDO = Cast<UChaosVehicleWheel>(WheelClass->GetDefaultObject(true));
            BaseWheelFriction[i] = WheelCDO ? WheelCDO->FrictionForceMultiplier : 2.0f; // 2.0 = UChaosVehicleWheel ctor default
        }
    }
    LastAppliedWheelFriction.Init(0.0f, NumWheels);

    for (int32 i = 0; i < NumWheels; ++i)
    {
        FChaosWheelSetup& Setup = WheeledComp->WheelSetups[i];
        UClass* WheelClass = Setup.WheelClass ? static_cast<UClass*>(Setup.WheelClass) : UChaosVehicleWheel::StaticClass();
        UChaosVehicleWheel* WheelCDO = Cast<UChaosVehicleWheel>(WheelClass->GetDefaultObject(true));
        if (!WheelCDO)
        {
            continue;
        }

        const float EffectiveFriction = BaseWheelFriction[i] * LateralGripMultiplier;

        // Static tire params on the wheel CDO. The Chaos wheel sim reads SideSlipModifier
        // (and Slip/SkidThreshold) live through a config pointer; GetPhysicsWheelConfig()
        // re-fills that config in place so the running sim picks the values up.
        WheelCDO->FrictionForceMultiplier = EffectiveFriction;
        WheelCDO->SideSlipModifier = DriftGripRetention;
        WheelCDO->bABSEnabled = bEnableABS;
        WheelCDO->GetPhysicsWheelConfig();

        // Keep the per-instance wheel object (Wheels[i]) consistent for debug/telemetry reads.
        if (WheeledComp->Wheels.IsValidIndex(i) && WheeledComp->Wheels[i])
        {
            WheeledComp->Wheels[i]->FrictionForceMultiplier = EffectiveFriction;
            WheeledComp->Wheels[i]->SideSlipModifier = DriftGripRetention;
            WheeledComp->Wheels[i]->bABSEnabled = bEnableABS;
        }

        // FrictionMultiplier is COPIED into the physics sim at vehicle creation, so the
        // CDO edit alone is not enough — push it through the runtime setter (physics-thread safe).
        // No-op if the physics state is not created yet; creation then snapshots the CDO value above.
        WheeledComp->SetWheelFrictionMultiplier(i, EffectiveFriction);
        WheeledComp->SetABSEnabled(i, bEnableABS);
        LastAppliedWheelFriction[i] = EffectiveFriction;
    }

    // Optional speed-sensitive steering assist. SteeringSetup.GetPhysicsSteeringConfig()
    // re-fills the steering config in place; the steering sim reads it live via pointer.
    if (bUseArcadeSteeringCurve)
    {
        FRichCurve* SrcCurve = ArcadeSteeringCurve.GetRichCurve();
        if (SrcCurve && SrcCurve->GetNumKeys() > 0)
        {
            FRichCurve* DstCurve = WheeledComp->SteeringSetup.SteeringCurve.GetRichCurve();
            DstCurve->Reset();
            for (auto KeyIt = SrcCurve->GetKeyHandleIterator(); KeyIt; ++KeyIt)
            {
                const FRichCurveKey& Key = SrcCurve->GetKey(*KeyIt);
                DstCurve->AddKey(Key.Time, Key.Value);
            }
            // GetWheelLayoutDimensions() is protected on the component; replicate
            // UChaosWheeledVehicleMovementComponent::CalculateWheelLayoutDimensions()
            // here using the public LocateBoneOffset() helper (full width/length, not half).
            FVector2D LayoutDims(0.f, 0.f);
            for (const FChaosWheelSetup& WheelSetup : WheeledComp->WheelSetups)
            {
                UClass* WheelClass = WheelSetup.WheelClass ? static_cast<UClass*>(WheelSetup.WheelClass) : UChaosVehicleWheel::StaticClass();
                const UChaosVehicleWheel* WheelCDO = Cast<UChaosVehicleWheel>(WheelClass->GetDefaultObject(true));
                const FVector ExtraOffset = (WheelCDO ? WheelCDO->Offset : FVector::ZeroVector) + WheelSetup.AdditionalOffset;
                const FVector RestingPos = WheeledComp->LocateBoneOffset(WheelSetup.BoneName, ExtraOffset);
                LayoutDims.X = FMath::Max(LayoutDims.X, FMath::Abs(RestingPos.X));
                LayoutDims.Y = FMath::Max(LayoutDims.Y, FMath::Abs(RestingPos.Y));
            }
            LayoutDims *= 2.0f;
            WheeledComp->SteeringSetup.GetPhysicsSteeringConfig(LayoutDims);
        }
    }

    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Arcade handling applied: grip x%.2f, drift retention %.2f, drift scale %.2f past %.0f deg, speed reduction %.2f @ %.0f km/h, ABS %d, steering curve %d"),
        LateralGripMultiplier, DriftGripRetention, DriftFrictionScale, DriftAngleThresholdDeg,
        SpeedGripReductionFactor, SpeedGripReductionMaxSpeedKmh, bEnableABS ? 1 : 0, bUseArcadeSteeringCurve ? 1 : 0);
}

void AChaosVehiclePawn::UpdateArcadeGrip(UChaosWheeledVehicleMovementComponent* WheeledComp, float DeltaTime)
{
    if (!WheeledComp || BaseWheelFriction.Num() == 0)
        return;

    // Speed-sensitive grip reduction: linear falloff up to SpeedGripReductionMaxSpeedKmh.
    const float SpeedKmh = GetSpeedKmh();
    const float SpeedAlpha = FMath::Clamp(SpeedKmh / FMath::Max(SpeedGripReductionMaxSpeedKmh, 1.0f), 0.0f, 1.0f);
    const float SpeedGripScale = 1.0f - SpeedGripReductionFactor * SpeedAlpha;

    // Drift grip: ease toward DriftFrictionScale while sliding past the threshold.
    const float DriftTarget = (FMath::Abs(CalculateDriftAngle()) > DriftAngleThresholdDeg) ? DriftFrictionScale : 1.0f;
    CurrentDriftGripScale = FMath::FInterpTo(CurrentDriftGripScale, DriftTarget, DeltaTime, 3.0f);

    const int32 NumWheels = FMath::Min(BaseWheelFriction.Num(), WheeledComp->WheelSetups.Num());
    for (int32 i = 0; i < NumWheels; ++i)
    {
        const float Target = BaseWheelFriction[i] * LateralGripMultiplier * SpeedGripScale * CurrentDriftGripScale;
        // Only push when the change is meaningful; each call enqueues a physics command.
        if (FMath::Abs(Target - LastAppliedWheelFriction[i]) > 0.01f)
        {
            WheeledComp->SetWheelFrictionMultiplier(i, Target);
            LastAppliedWheelFriction[i] = Target;
        }
    }
}

void AChaosVehiclePawn::Tick(float DeltaTime)
{
    if (bDriveOverride)
    {
        CurrentThrottle = OverrideThrottle;
        CurrentSteering = OverrideSteering;
        CurrentBrake = OverrideBrake;
        bHandbrake = bOverrideHandbrake;
        if (GetSpeedKmh() < 8.f)
        {
            // Wake bodies/sleep only — NEVER EnsureDefaultWheels/Recreate every tick
            // (shared WheelClass CDOs flip AxleType Front<->Rear and zero drvTq).
            if (auto* MoveWake = GetVehicleMovementComponent())
            {
                MoveWake->SetParked(false);
                MoveWake->SetSleeping(false);
                MoveWake->SetHandbrakeInput(bHandbrake);
            }
            if (USkeletalMeshComponent* Skel = GetMesh())
            {
                Skel->WakeAllRigidBodies();
            }
        }
        if (auto* MoveCompEarly = GetVehicleMovementComponent())
        {
            MoveCompEarly->SetRequiresControllerForInputs(false);
            MoveCompEarly->SetThrottleInput(CurrentThrottle * ThrottleSensitivity);
            MoveCompEarly->SetSteeringInput(CurrentSteering * SteeringSensitivity);
            MoveCompEarly->SetBrakeInput(CurrentBrake);
            MoveCompEarly->SetHandbrakeInput(bHandbrake);
            if (auto* WheeledEarly = Cast<UChaosWheeledVehicleMovementComponent>(MoveCompEarly))
            {
                if (WheeledEarly->GetCurrentGear() <= 0 && CurrentThrottle > 0.1f)
                {
                    WheeledEarly->SetTargetGear(1, true);
                }
                // Arcade Cleveland: Chaos TorqueRatio can latch at 0 after shared-CDO recreate.
                // Additive drive torque every crawl/race frame: engine power still flows when the
                // drivetrain works (Override capped the car at MaxTorque/4 per wheel ~23 km/h),
                // and the push remains as a floor if TorqueRatio latches again.
                const float Thr = FMath::Clamp(CurrentThrottle * ThrottleSensitivity, 0.f, 1.f);
                const int32 NumW = WheeledEarly->Wheels.Num();
                if (NumW > 0 && Thr > 0.05f && CurrentBrake < 0.15f && !bHandbrake)
                {
                    const float PerWheelNm = (WheeledEarly->EngineSetup.MaxTorque * Thr) / float(NumW);
                    for (int32 wi = 0; wi < NumW; ++wi)
                    {
                        WheeledEarly->SetTorqueCombineMethod(ETorqueCombineMethod::Additive, wi);
                        WheeledEarly->SetDriveTorque(PerWheelNm, wi);
                    }
                }
                else if (NumW > 0)
                {
                    for (int32 wi = 0; wi < NumW; ++wi)
                    {
                        WheeledEarly->SetDriveTorque(0.f, wi);
                    }
                }
            }
        }
    }
    Super::Tick(DeltaTime);
    if (bClevelandShowcaseChaseFraming)
    {
        UpdateClevelandShowcaseChaseFraming();
    }

    auto* MoveComp = GetVehicleMovementComponent();
    if (MoveComp)
    {
        float FinalThrottle = CurrentThrottle * ThrottleSensitivity;
        float FinalSteering = CurrentSteering * SteeringSensitivity;

        // Drift assist: apply counter-steer when handbrake is active and sliding
        if (bHandbrake && TuningData)
        {
            float DriftAngle = CalculateDriftAngle();
            if (FMath::Abs(DriftAngle) > 5.0f)
            {
                float CounterSteer = -FMath::Sign(DriftAngle) * TuningData->CounterSteerGain * FMath::Clamp(FMath::Abs(DriftAngle) / TuningData->DriftAngleMax, 0.0f, 1.0f);
                FinalSteering = FMath::Lerp(FinalSteering, CounterSteer, 0.3f);
            }

        }

        // Traction control: reduce throttle when wheel slip is high
        if (TuningData && TuningData->TractionControl > 0.0f)
        {
            float SlipRatio = CalculateWheelSlipRatio();
            if (SlipRatio > 0.25f)
            {
                float TCTarget = FMath::Lerp(1.0f, 0.7f, TuningData->TractionControl);
                // More slip -> more cut (was inverted: full throttle returned above 0.5 slip).
                FinalThrottle *= FMath::Lerp(1.0f, TCTarget, FMath::Clamp((SlipRatio - 0.25f) / 0.25f, 0.0f, 1.0f));
            }
        }

        MoveComp->SetThrottleInput(FinalThrottle);
        MoveComp->SetSteeringInput(FinalSteering);
        MoveComp->SetBrakeInput(CurrentBrake);
        MoveComp->SetHandbrakeInput(bHandbrake);

        // Dynamic arcade grip: speed-sensitive reduction + drift friction scale
        if (bEnableArcadeHandling)
        {
            if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
            {
                UpdateArcadeGrip(WheeledComp, DeltaTime);
                // Non-override path: same arcade drive push (player possessed).
                {
                    const float Thr = FMath::Clamp(CurrentThrottle * ThrottleSensitivity, 0.f, 1.f);
                    const int32 NumW = WheeledComp->Wheels.Num();
                    if (NumW > 0 && Thr > 0.05f && CurrentBrake < 0.15f && !bHandbrake)
                    {
                        const float PerWheelNm = (WheeledComp->EngineSetup.MaxTorque * Thr) / float(NumW);
                        for (int32 wi = 0; wi < NumW; ++wi)
                        {
                            WheeledComp->SetTorqueCombineMethod(ETorqueCombineMethod::Additive, wi);
                            WheeledComp->SetDriveTorque(PerWheelNm, wi);
                        }
                    }
                }
            }
        }
    }

    // Update audio with brake state
    if (AudioComponent)
    {
        AudioComponent->SetBrakeInput(CurrentBrake);
    }

    // Update HUD telemetry
    if (APlayerController* PC = Cast<APlayerController>(GetController()))
    {
        if (ANeonHUD* HUD = Cast<ANeonHUD>(PC->GetHUD()))
        {
            HUD->SetSpeedKmh(GetSpeedKmh());
            HUD->SetTelemetry(GetEngineRPM(), GetCurrentGear());
        }
    }
}

void AChaosVehiclePawn::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
    Super::SetupPlayerInputComponent(PlayerInputComponent);

    PlayerInputComponent->BindAxis(TEXT("Throttle"), this, &AChaosVehiclePawn::SetThrottleInput);
    PlayerInputComponent->BindAxis(TEXT("Steer"), this, &AChaosVehiclePawn::SetSteeringInput);
    PlayerInputComponent->BindAxis(TEXT("Brake"), this, &AChaosVehiclePawn::SetBrakeInput);
    PlayerInputComponent->BindAction(TEXT("Handbrake"), IE_Pressed, this, &AChaosVehiclePawn::HandbrakePressed);
    PlayerInputComponent->BindAction(TEXT("Handbrake"), IE_Released, this, &AChaosVehiclePawn::HandbrakeReleased);
    PlayerInputComponent->BindAction(TEXT("ResetVehicle"), IE_Pressed, this, &AChaosVehiclePawn::ResetVehicle);
    PlayerInputComponent->BindAction(TEXT("ToggleCamera"), IE_Pressed, this, &AChaosVehiclePawn::ToggleCamera);
}

void AChaosVehiclePawn::SetThrottleInput(float Value)
{
    if (bDriveOverride)
    {
        return;
    }
    CurrentThrottle = FMath::Clamp(Value, -1.0f, 1.0f);
}

void AChaosVehiclePawn::SetSteeringInput(float Value)
{
    if (bDriveOverride)
    {
        return;
    }
    CurrentSteering = FMath::Clamp(Value, -1.0f, 1.0f);
}

void AChaosVehiclePawn::SetBrakeInput(float Value)
{
    if (bDriveOverride)
    {
        return;
    }
    CurrentBrake = FMath::Clamp(Value, 0.0f, 1.0f);
}

void AChaosVehiclePawn::SetHandbrakeInput(bool bActive)
{
    if (bDriveOverride)
    {
        return;
    }
    bHandbrake = bActive;
}

void AChaosVehiclePawn::SetDriveOverride(float Steer, float Throttle, float Brake, bool bInHandbrake)
{
    bDriveOverride = true;
    OverrideSteering = FMath::Clamp(Steer, -1.0f, 1.0f);
    OverrideThrottle = FMath::Clamp(Throttle, -1.0f, 1.0f);
    OverrideBrake = FMath::Clamp(Brake, 0.0f, 1.0f);
    bOverrideHandbrake = bInHandbrake;
    CurrentSteering = OverrideSteering;
    CurrentThrottle = OverrideThrottle;
    CurrentBrake = OverrideBrake;
    bHandbrake = bOverrideHandbrake;
    if (auto* MoveComp = GetVehicleMovementComponent())
    {
        MoveComp->SetSteeringInput(CurrentSteering * SteeringSensitivity);
        MoveComp->SetThrottleInput(CurrentThrottle * ThrottleSensitivity);
        MoveComp->SetBrakeInput(CurrentBrake);
        MoveComp->SetHandbrakeInput(bHandbrake);
    }
}

void AChaosVehiclePawn::ReleaseForRace()
{
    // Clears AI Hold SetDriveOverride(0,0,brake=1,hb=true). Override ignores SetHandbrakeInput.
    WakeForDrive();
    if (bDriveOverride)
    {
        SetDriveOverride(OverrideSteering, FMath::Max(OverrideThrottle, 0.f), 0.f, false);
    }
    else
    {
        CurrentBrake = 0.f;
        bHandbrake = false;
        if (auto* MoveComp = GetVehicleMovementComponent())
        {
            MoveComp->SetHandbrakeInput(false);
            MoveComp->SetBrakeInput(0.f);
        }
    }
    if (auto* MoveComp = GetVehicleMovementComponent())
    {
        MoveComp->SetRequiresControllerForInputs(false);
        MoveComp->SetHandbrakeInput(false);
        MoveComp->SetBrakeInput(0.f);
        MoveComp->SetParked(false);
        MoveComp->SetSleeping(false);
        if (auto* Wheeled = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
        {
            // Do NOT RecreatePhysicsState here — mid-grid recreate collapses suspension (sus=-10)
            // and can yeet/crash the pawn. Engine must be armed in BeginPlay already.
            EnsureEngineDriveConfig();
            Wheeled->EnableMechanicalSim(true);
            Wheeled->SetTargetGear(1, true);
            Wheeled->SetHandbrakeInput(false);
            Wheeled->SetBrakeInput(0.f);
            AssertMoveCompTickAfterPawn();
            bChaosSimReady = true;
        }
    }
}

void AChaosVehiclePawn::ClearDriveOverride()
{
    bDriveOverride = false;
}

void AChaosVehiclePawn::EnsureDefaultWheels()
{
    auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    if (!WheeledComp)
    {
        return;
    }
    if (WheeledComp->WheelSetups.Num() > 0)
    {
        // Distinct Front/Rear WheelClass CDOs so AWD/RWD TorqueRatio != 0. One-shot only.
        FString BoneDump;
        for (int32 i = 0; i < WheeledComp->WheelSetups.Num(); ++i)
        {
            BoneDump += WheeledComp->WheelSetups[i].BoneName.ToString() + TEXT(",");
        }

        if (!bAuthoredWheelsTorqueFixed)
        {
            for (int32 i = 0; i < WheeledComp->WheelSetups.Num(); ++i)
            {
                FChaosWheelSetup& Setup = WheeledComp->WheelSetups[i];
                Setup.WheelClass = (i < 2)
                    ? URaceGPSVehicleWheelFront::StaticClass()
                    : URaceGPSVehicleWheelRear::StaticClass();
            }
            if (WheeledComp->DifferentialSetup.FrontRearSplit < 0.05f
                || WheeledComp->DifferentialSetup.FrontRearSplit > 0.95f)
            {
                WheeledComp->DifferentialSetup.FrontRearSplit = 0.5f;
            }
            WheeledComp->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
            EnsureEngineDriveConfig();
            WheeledComp->EnableMechanicalSim(true);
            WheeledComp->RecreatePhysicsState();
            AssertMoveCompTickAfterPawn();
            EnsureEngineDriveConfig();
            WheeledComp->EnableMechanicalSim(true);
            bAuthoredWheelsTorqueFixed = true;
            bDriveWheelsPatched = true;
            UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: authored wheels torque-fix once pawn=%s runtime=%d bones=%s"),
                *GetName(), WheeledComp->Wheels.Num(), *BoneDump);
        }

        for (int32 i = 0; i < WheeledComp->Wheels.Num(); ++i)
        {
            if (UChaosVehicleWheel* W = WheeledComp->Wheels[i])
            {
                W->bAffectedByEngine = true;
                W->bAffectedByBrake = true;
                W->bAffectedBySteering = (i < 2);
                W->MaxSteerAngle = (i < 2) ? 40.f : 0.f;
                W->bAffectedByHandbrake = (i >= 2);
            }
        }
        WheeledComp->SetParked(false);
        WheeledComp->SetSleeping(false);
        bChaosSimReady = true;
        return;
    }

    USkeletalMeshComponent* Skel = GetMesh();
    TArray<FName> Bones;
    if (Skel)
    {
        Skel->GetBoneNames(Bones);
    }

    auto PickBone = [&](const TArray<FName>& Exact, const TArray<FString>& MustAll, FName& Out) -> bool
    {
        for (const FName& Want : Exact)
        {
            if (Bones.Contains(Want))
            {
                Out = Want;
                return true;
            }
        }
        for (const FName& Bone : Bones)
        {
            const FString N = Bone.ToString();
            bool bAll = true;
            for (const FString& Token : MustAll)
            {
                if (!N.Contains(Token, ESearchCase::IgnoreCase))
                {
                    bAll = false;
                    break;
                }
            }
            if (bAll && MustAll.Num() > 0)
            {
                Out = Bone;
                return true;
            }
        }
        return false;
    };

    FName FL, FR, RL, RR;
    const bool bFL = PickBone(
        { TEXT("Wheel_Front_Left"), TEXT("wheel_front_left") },
        { TEXT("Front"), TEXT("Left"), TEXT("Wheel") }, FL);
    const bool bFR = PickBone(
        { TEXT("Wheel_Front_Right"), TEXT("wheel_front_right") },
        { TEXT("Front"), TEXT("Right"), TEXT("Wheel") }, FR);
    const bool bRL = PickBone(
        { TEXT("Wheel_Rear_Left"), TEXT("wheel_rear_left") },
        { TEXT("Rear"), TEXT("Left"), TEXT("Wheel") }, RL);
    const bool bRR = PickBone(
        { TEXT("Wheel_Rear_Right"), TEXT("wheel_rear_right") },
        { TEXT("Rear"), TEXT("Right"), TEXT("Wheel") }, RR);

    FString BoneList;
    for (const FName& Bone : Bones)
    {
        BoneList += Bone.ToString() + TEXT(",");
    }
    UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: mesh bones (%d) %s"), Bones.Num(), *BoneList);

    struct FSeed { FName Bone; FVector Offset; bool bSteer; };
    const FSeed Seeds[4] = {
        { bFL ? FL : NAME_None, FVector(140.f,  80.f, 0.f), true },
        { bFR ? FR : NAME_None, FVector(140.f, -80.f, 0.f), true },
        { bRL ? RL : NAME_None, FVector(-140.f,  80.f, 0.f), false },
        { bRR ? RR : NAME_None, FVector(-140.f, -80.f, 0.f), false },
    };

    WheeledComp->WheelSetups.Reset();
    for (int32 i = 0; i < 4; ++i)
    {
        FChaosWheelSetup Setup;
        Setup.WheelClass = (i < 2)
            ? URaceGPSVehicleWheelFront::StaticClass()
            : URaceGPSVehicleWheelRear::StaticClass();
        Setup.BoneName = Seeds[i].Bone;
        Setup.AdditionalOffset = Seeds[i].Bone.IsNone() ? Seeds[i].Offset : FVector::ZeroVector;
        WheeledComp->WheelSetups.Add(Setup);
    }

    UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: synthesized 4 WheelSetups pawn=%s bones FL=%s FR=%s RL=%s RR=%s boneCount=%d"),
        *GetName(), *FL.ToString(), *FR.ToString(), *RL.ToString(), *RR.ToString(), Bones.Num());

    WheeledComp->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
    WheeledComp->EngineSetup.MaxTorque = 700.f;
    WheeledComp->EngineSetup.MaxRPM = 6500.f;
    WheeledComp->TransmissionSetup.bUseAutomaticGears = true;
    if (Skel)
    {
        Skel->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        Skel->SetSimulatePhysics(true);
        UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: mesh PA=%d simulating=%d pawn=%s"),
            Skel->GetPhysicsAsset() ? 1 : 0, Skel->IsSimulatingPhysics() ? 1 : 0, *GetName());
    }

    EnsureEngineDriveConfig();
    WheeledComp->RecreatePhysicsState();
    AssertMoveCompTickAfterPawn();
    EnsureEngineDriveConfig();
    for (int32 i = 0; i < WheeledComp->Wheels.Num(); ++i)
    {
        if (UChaosVehicleWheel* W = WheeledComp->Wheels[i])
        {
            W->bAffectedByEngine = true;
            W->bAffectedByBrake = true;
            W->bAffectedBySteering = (i < 2);
            W->MaxSteerAngle = (i < 2) ? 40.f : 0.f;
            W->bAffectedByHandbrake = (i >= 2);
            W->GetPhysicsWheelConfig();
        }
    }
    WheeledComp->SetParked(false);
    WheeledComp->SetSleeping(false);
    bDriveWheelsPatched = true;
    bChaosSimReady = true;
}

void AChaosVehiclePawn::WakeForDrive()
{
    if (USkeletalMeshComponent* Skel = GetMesh())
    {
        Skel->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
        Skel->SetSimulatePhysics(true);
        Skel->WakeAllRigidBodies();
        if (FBodyInstance* BI = Skel->GetBodyInstance())
        {
            BI->SetInstanceSimulatePhysics(true);
            BI->WakeInstance();
        }
    }
    // Slim wake for crawl frames: bodies + park/sleep + gear ONLY.
    // Do NOT call EnsureDefaultWheels / Recreate here (shared-CDO thrash / recreate storm).
    OverrideBrake = 0.f;
    bOverrideHandbrake = false;
    CurrentBrake = 0.f;
    bHandbrake = false;
    if (auto* MoveComp = GetVehicleMovementComponent())
    {
        MoveComp->SetRequiresControllerForInputs(false);
        MoveComp->SetBrakeInput(0.f);
        MoveComp->SetHandbrakeInput(false);
        MoveComp->SetParked(false);
        MoveComp->SetSleeping(false);
        if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
        {
            if (WheeledComp->GetCurrentGear() <= 0)
            {
                WheeledComp->SetTargetGear(1, true);
            }
        }
        if (UPrimitiveComponent* Prim = Cast<UPrimitiveComponent>(MoveComp->UpdatedComponent))
        {
            Prim->SetSimulatePhysics(true);
            Prim->WakeAllRigidBodies();
        }
    }
    AssertMoveCompTickAfterPawn();
}

void AChaosVehiclePawn::CloseVehicleDoors()
{
    // VISUAL FLOOR 2026-09-24: CARLA Charger doors are SEPARATE static meshes.
    // Morph/AnimBP flags cannot restore missing door geometry — attach SMs instead.
    EnsureCarlaChargerDoors();
    USkeletalMeshComponent* Skel = GetMesh();
    if (!Skel)
    {
        return;
    }
    static const FName DoorBones[] = {
        TEXT("Door_FL"), TEXT("Door_FR"), TEXT("Door_RL"), TEXT("Door_RR"),
        TEXT("Door_Front_Left"), TEXT("Door_Front_Right"),
        TEXT("Door_Back_Left"), TEXT("Door_Back_Right"),
        TEXT("Door_Rear_Left"), TEXT("Door_Rear_Right")
    };
    int32 Closed = 0;
    for (const FName& Bone : DoorBones)
    {
        if (Skel->GetBoneIndex(Bone) == INDEX_NONE)
        {
            continue;
        }
        // UE5.7: no SetBoneRotationByName on USkeletalMeshComponent; door SMs carry pose.
        ++Closed;
    }
    for (UStaticMeshComponent* DoorMesh : CarlaDoorMeshes)
    {
        if (DoorMesh)
        {
            DoorMesh->SetRelativeRotation(FRotator::ZeroRotator);
            DoorMesh->SetVisibility(true);
        }
    }
    if (UAnimInstance* Anim = Skel->GetAnimInstance())
    {
        static const FName Flags[] = {
            TEXT("bOpenDoors"), TEXT("OpenDoors"), TEXT("bDoorsOpen"), TEXT("DoorsOpen"),
            TEXT("bOpenDoorFL"), TEXT("bOpenDoorFR"), TEXT("bOpenDoorRL"), TEXT("bOpenDoorRR")
        };
        for (const FName& Flag : Flags)
        {
            if (FBoolProperty* Prop = FindFProperty<FBoolProperty>(Anim->GetClass(), Flag))
            {
                Prop->SetPropertyValue_InContainer(Anim, false);
            }
        }
    }
    UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: CloseVehicleDoors bones=%d doorMeshes=%d on %s"),
        Closed, CarlaDoorMeshes.Num(), *GetName());
}

void AChaosVehiclePawn::EnsureCarlaChargerDoors()
{
    USkeletalMeshComponent* Skel = GetMesh();
    if (!Skel)
    {
        return;
    }
    if (CarlaDoorMeshes.Num() > 0)
    {
        return; // already attached
    }

    struct FDoorAttach
    {
        const TCHAR* MeshPath;
        const TCHAR* CompName;
        const TCHAR* BonePrimary;
        const TCHAR* BoneAlt;
    };
    // Paths match CARLA 0.10.0 package names under Content/Carla/Static/...
    static const FDoorAttach Parts[] = {
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorFL.SM_DodgeCharger2024_DoorFL"),
          TEXT("CarlaDoorFL"), TEXT("Door_FL"), TEXT("Door_Front_Left") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorFR.SM_DodgeCharger2024_DoorFR"),
          TEXT("CarlaDoorFR"), TEXT("Door_FR"), TEXT("Door_Front_Right") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorRL.SM_DodgeCharger2024_DoorRL"),
          TEXT("CarlaDoorRL"), TEXT("Door_RL"), TEXT("Door_Back_Left") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_DoorRR.SM_DodgeCharger2024_DoorRR"),
          TEXT("CarlaDoorRR"), TEXT("Door_RR"), TEXT("Door_Back_Right") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/SM_DodgeCharger2024_Lights.SM_DodgeCharger2024_Lights"),
          TEXT("CarlaLights"), TEXT("Vehicle_Base"), TEXT("VehicleBase") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Glass/SM_GlassExt_Dodge2024.SM_GlassExt_Dodge2024"),
          TEXT("CarlaGlassExt"), TEXT("Vehicle_Base"), TEXT("VehicleBase") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Glass/SM_GlassExt2_Dodge2024.SM_GlassExt2_Dodge2024"),
          TEXT("CarlaGlassExt2"), TEXT("Vehicle_Base"), TEXT("VehicleBase") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Glass/SM_GlassInt1_Dodge2024.SM_GlassInt1_Dodge2024"),
          TEXT("CarlaGlassInt1"), TEXT("Vehicle_Base"), TEXT("VehicleBase") },
        { TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Glass/SM_GlassInt2_Dodge2024.SM_GlassInt2_Dodge2024"),
          TEXT("CarlaGlassInt2"), TEXT("Vehicle_Base"), TEXT("VehicleBase") },
    };

    int32 Attached = 0;
    int32 Missing = 0;
    for (const FDoorAttach& Part : Parts)
    {
        UStaticMesh* PartMesh = LoadObject<UStaticMesh>(nullptr, Part.MeshPath);
        if (!PartMesh)
        {
            ++Missing;
            UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: missing CARLA part %s"), Part.MeshPath);
            continue;
        }
        FName Socket = Part.BonePrimary;
        if (Skel->GetBoneIndex(Socket) == INDEX_NONE)
        {
            Socket = Part.BoneAlt;
        }
        if (Skel->GetBoneIndex(Socket) == INDEX_NONE)
        {
            Socket = NAME_None; // attach to mesh root
        }
        UStaticMeshComponent* Comp = NewObject<UStaticMeshComponent>(this, Part.CompName);
        Comp->SetStaticMesh(PartMesh);
        Comp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
        Comp->SetGenerateOverlapEvents(false);
        Comp->SetCanEverAffectNavigation(false);
        Comp->SetMobility(EComponentMobility::Movable);
        if (Socket.IsNone())
        {
            Comp->SetupAttachment(Skel);
        }
        else
        {
            Comp->SetupAttachment(Skel, Socket);
        }
        Comp->SetRelativeLocation(FVector::ZeroVector);
        Comp->SetRelativeRotation(FRotator::ZeroRotator);
        Comp->SetRelativeScale3D(FVector::OneVector);
        Comp->RegisterComponent();
        Comp->SetVisibility(true);
        CarlaDoorMeshes.Add(Comp);
        ++Attached;
    }
    UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: EnsureCarlaChargerDoors attached=%d missing=%d pawn=%s"),
        Attached, Missing, *GetName());
    ApplyChargerVisualMaterialFloor();
}

void AChaosVehiclePawn::DumpDriveState(const TCHAR* Tag)
{
	USkeletalMeshComponent* Skel = GetMesh();
	auto* MoveComp = GetVehicleMovementComponent();
	bool bAwake = false;
	if (Skel)
	{
		if (FBodyInstance* BI = Skel->GetBodyInstance())
		{
			bAwake = BI->IsInstanceAwake();
		}
	}
	const int32 Parked = MoveComp && MoveComp->IsParked() ? 1 : 0;
	const int32 Simulating = (Skel && Skel->IsSimulatingPhysics()) ? 1 : 0;
	int32 Setups = 0;
	int32 RuntimeWheels = 0;
	float MaxTorque = 0.f;
	float MaxRPM = 0.f;
	int32 Gear = 0;
	int32 EngineOn = 0;
	int32 Mech = 0;
	float EngineRPM = 0.f;
	FString Bones;
	FString WheelDump;
	int32 ContactCount = 0;
	float MoveRawThr = 0.f;
	float MoveRawBrake = 0.f;
	float MoveRawSteer = 0.f;
	int32 MoveHb = 0;
	float MoveProcThr = -1.f;
	float MoveProcBrake = -1.f;
	float MoveProcHb = -1.f;
	int32 ReqCtrl = -1;
	int32 TickPrereqSelf = 0;
	int32 TickPrereqCount = 0;
	if (MoveComp)
	{
		MoveRawThr = MoveComp->GetThrottleInput();
		MoveRawBrake = MoveComp->GetBrakeInput();
		MoveRawSteer = MoveComp->GetSteeringInput();
		MoveHb = MoveComp->GetHandbrakeInput() ? 1 : 0;
		if (FFloatProperty* ThrProp = FindFProperty<FFloatProperty>(MoveComp->GetClass(), TEXT("ThrottleInput")))
		{
			MoveProcThr = ThrProp->GetPropertyValue_InContainer(MoveComp);
		}
		if (FFloatProperty* BrProp = FindFProperty<FFloatProperty>(MoveComp->GetClass(), TEXT("BrakeInput")))
		{
			MoveProcBrake = BrProp->GetPropertyValue_InContainer(MoveComp);
		}
		if (FFloatProperty* HbProp = FindFProperty<FFloatProperty>(MoveComp->GetClass(), TEXT("HandbrakeInput")))
		{
			MoveProcHb = HbProp->GetPropertyValue_InContainer(MoveComp);
		}
		if (FBoolProperty* ReqProp = FindFProperty<FBoolProperty>(MoveComp->GetClass(), TEXT("bRequiresControllerForInputs")))
		{
			ReqCtrl = ReqProp->GetPropertyValue_InContainer(MoveComp) ? 1 : 0;
		}
		const TArray<struct FTickPrerequisite>& Prereqs = MoveComp->PrimaryComponentTick.GetPrerequisites();
		TickPrereqCount = Prereqs.Num();
		for (const FTickPrerequisite& P : Prereqs)
		{
			if (P.PrerequisiteObject.Get() == this)
			{
				TickPrereqSelf = 1;
				break;
			}
		}
	}
	if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(MoveComp))
	{
		Setups = WheeledComp->WheelSetups.Num();
		RuntimeWheels = WheeledComp->Wheels.Num();
		MaxTorque = WheeledComp->EngineSetup.MaxTorque;
		MaxRPM = WheeledComp->EngineSetup.MaxRPM;
		Gear = WheeledComp->GetCurrentGear();
		Mech = WheeledComp->bMechanicalSimEnabled ? 1 : 0;
		EngineRPM = WheeledComp->GetEngineRotationSpeed();
		for (int32 i = 0; i < WheeledComp->WheelSetups.Num(); ++i)
		{
			const FChaosWheelSetup& Setup = WheeledComp->WheelSetups[i];
			const int32 Aff = (WheeledComp->Wheels.IsValidIndex(i) && WheeledComp->Wheels[i] && WheeledComp->Wheels[i]->bAffectedByEngine) ? 1 : 0;
			EngineOn += Aff;
			Bones += FString::Printf(TEXT("%s(eng=%d off=%.0f,%.0f,%.0f),"),
				*Setup.BoneName.ToString(), Aff,
				Setup.AdditionalOffset.X, Setup.AdditionalOffset.Y, Setup.AdditionalOffset.Z);
		}
		for (int32 i = 0; i < RuntimeWheels; ++i)
		{
			const FWheelStatus& WS = WheeledComp->GetWheelState(i);
			if (WS.bInContact) { ++ContactCount; }
			const float Susp = WheeledComp->GetSuspensionOffset(i);
			WheelDump += FString::Printf(TEXT("w%d:c=%d sus=%.1f nLen=%.2f spr=%.0f drvTq=%.0f;"),
				i, WS.bInContact ? 1 : 0, Susp, WS.NormalizedSuspensionLength, WS.SpringForce, WS.DriveTorque);
		}
	}
	UE_LOG(LogTemp, Warning,
		TEXT("raceGPS Cleveland drive-dump %s class=%s pawn=%s speed=%.2f pawnThr=%.2f moveRawThr=%.2f moveProcThr=%.2f brakeP=%.2f/raw=%.2f/proc=%.2f hbP=%d/raw=%d/proc=%.2f override=%d awake=%d sim=%d parked=%d mech=%d reqCtrl=%d tickPrereq=%d/%d wheels=%d/%d contact=%d engOn=%d tq=%.0f maxrpm=%.0f rpm=%.0f gear=%d fwd=%.1f z=%.1f bones=%s wheelsDetail=%s move=%s ctrl=%s"),
		Tag ? Tag : TEXT("?"),
		*GetNameSafe(GetClass()),
		*GetName(),
		GetSpeedKmh(),
		CurrentThrottle,
		MoveRawThr,
		MoveProcThr,
		CurrentBrake,
		MoveRawBrake,
		MoveProcBrake,
		bHandbrake ? 1 : 0,
		MoveHb,
		MoveProcHb,
		bDriveOverride ? 1 : 0,
		bAwake ? 1 : 0,
		Simulating,
		Parked,
		Mech,
		ReqCtrl,
		TickPrereqSelf,
		TickPrereqCount,
		RuntimeWheels, Setups,
		ContactCount,
		EngineOn,
		MaxTorque,
		MaxRPM,
		EngineRPM,
		Gear,
		MoveComp ? MoveComp->GetForwardSpeed() : 0.f,
		GetActorLocation().Z,
		*Bones,
		*WheelDump,
		*GetNameSafe(MoveComp),
		*GetNameSafe(GetController()));
}

void AChaosVehiclePawn::HandbrakePressed()
{
    bHandbrake = true;
}

void AChaosVehiclePawn::HandbrakeReleased()
{
    bHandbrake = false;
}

void AChaosVehiclePawn::ResetVehicle()
{
    auto* MoveComp = GetVehicleMovementComponent();
    if (MoveComp)
    {
        MoveComp->StopMovementImmediately();
    }

    FVector CurrentLocation = GetActorLocation();
    FRotator CurrentRotation = GetActorRotation();
    CurrentLocation.Z += 50.0f;
    SetActorLocationAndRotation(CurrentLocation, CurrentRotation, false, nullptr, ETeleportType::ResetPhysics);
}

void AChaosVehiclePawn::ToggleCamera()
{
    ActiveCameraIndex = (ActiveCameraIndex + 1) % 2;
    ApplyVehicleLook(VehicleLook);
    UpdateCameraView();
}

void AChaosVehiclePawn::UpdateCameraView()
{
    if (ActiveCameraIndex == 0)
    {
        ChaseCamera->SetActive(true);
        HoodCamera->SetActive(false);
        SpringArm->SetActive(true);
    }
    else
    {
        ChaseCamera->SetActive(false);
        HoodCamera->SetActive(true);
        SpringArm->SetActive(false);
    }
}


void AChaosVehiclePawn::UpdateClevelandShowcaseChaseFraming()
{
    // V16: race follow — no world-south look-at into empty void.
    // SpringArm inherits yaw; keep a stable mild dive on the car.
    if (!SpringArm || !bClevelandShowcaseChaseFraming)
    {
        return;
    }
    const FRotator Rel = SpringArm->GetRelativeRotation();
    const float DesiredPitch = -12.0f;
    if (!FMath::IsNearlyEqual(Rel.Pitch, DesiredPitch, 0.05f) || !FMath::IsNearlyZero(Rel.Roll, 0.05f))
    {
        SpringArm->SetRelativeRotation(FRotator(DesiredPitch, 0.0f, 0.0f));
    }
}

void AChaosVehiclePawn::ApplyClevelandShowcaseChaseFraming()
{
    if (!SpringArm || !ChaseCamera)
    {
        return;
    }
    // V16 RACE-FOLLOW: sit behind the car, inherit yaw, kill absolute world-south lock
    // that was framing black void when downtown/-Y wasn't lit in view.
    bClevelandShowcaseChaseFraming = true;
    SpringArm->bUsePawnControlRotation = false;
    SpringArm->bInheritPitch = false;
    SpringArm->bInheritRoll = false;
    SpringArm->bInheritYaw = true;
    SpringArm->SetUsingAbsoluteRotation(false);
    SpringArm->TargetArmLength = 680.0f;
    SpringArm->SocketOffset = FVector(0.0f, 0.0f, 140.0f);
    SpringArm->TargetOffset = FVector(40.0f, 0.0f, 35.0f);
    SpringArm->bDoCollisionTest = false;
    SpringArm->ProbeSize = 16.0f;
    SpringArm->SetRelativeRotation(FRotator(-12.0f, 0.0f, 0.0f));
    ChaseCamera->SetFieldOfView(75.0f);
    ChaseCamera->bUsePawnControlRotation = false;
    ActiveCameraIndex = 0;
    UpdateCameraView();
    UpdateClevelandShowcaseChaseFraming();
    const FRotator ArmW = SpringArm->GetComponentRotation();
    const FRotator PawnW = GetActorRotation();
    UE_LOG(LogTemp, Log, TEXT("raceGPS Cleveland: applied chase framing V16 RACE-FOLLOW arm=680 FOV=75 pawnYaw=%.1f armYaw=%.1f armPitch=%.1f (behind car, no void lock)"),
        PawnW.Yaw, ArmW.Yaw, ArmW.Pitch);
}

float AChaosVehiclePawn::GetSpeedKmh() const
{
    return GetVelocity().Size() * 0.036f;
}

float AChaosVehiclePawn::GetEngineRPM() const
{
    auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    return WheeledComp ? WheeledComp->GetEngineRotationSpeed() : 0.0f;
}

int32 AChaosVehiclePawn::GetCurrentGear() const
{
    auto* MoveComp = GetVehicleMovementComponent();
    return MoveComp ? MoveComp->GetCurrentGear() : 0;
}

float AChaosVehiclePawn::CalculateDriftAngle() const
{
    FVector Velocity = GetVelocity();
    FVector Forward = GetActorForwardVector();
    Forward.Z = 0.0f;
    Forward.Normalize();
    Velocity.Z = 0.0f;

    float ForwardSpeed = FVector::DotProduct(Velocity, Forward);
    float TotalSpeed = Velocity.Size();

    if (TotalSpeed < 1.0f)
        return 0.0f;

    float CosAngle = ForwardSpeed / TotalSpeed;
    float AngleRad = FMath::Acos(FMath::Clamp(CosAngle, -1.0f, 1.0f));
    float AngleDeg = FMath::RadiansToDegrees(AngleRad);

    // Determine direction (left or right drift)
    FVector Right = GetActorRightVector();
    Right.Z = 0.0f;
    Right.Normalize();
    float LateralSpeed = FVector::DotProduct(Velocity, Right);

    return FMath::Sign(LateralSpeed) * AngleDeg;
}

float AChaosVehiclePawn::CalculateWheelSlipRatio() const
{
    auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent());
    if (!WheeledComp)
        return 0.0f;

    float MaxSlip = 0.0f;
    float LinearSpeed = FMath::Max(GetSpeedKmh() / 3.6f, 0.0f) * 100.0f; // cm/s (1 uu = 1 cm)
    for (UChaosVehicleWheel* Wheel : WheeledComp->Wheels)
    {
        if (!Wheel)
        {
            continue;
        }
        float WheelRadius = Wheel->WheelRadius; // cm
        float AngularSpeed = FMath::Abs(Wheel->GetWheelAngularVelocity()); // rad/s
        float TheoreticalSpeed = AngularSpeed * WheelRadius; // cm/s

        if (TheoreticalSpeed > 1.0f)
        {
            float Slip = FMath::Abs(TheoreticalSpeed - LinearSpeed) / TheoreticalSpeed;
            MaxSlip = FMath::Max(MaxSlip, Slip);
        }
    }
    return MaxSlip;
}

void AChaosVehiclePawn::OnVehicleHit(UPrimitiveComponent* HitComponent, AActor* OtherActor,
                                      UPrimitiveComponent* OtherComp, FVector NormalImpulse,
                                      const FHitResult& Hit)
{
    if (!OtherActor || OtherActor == this)
        return;

    float ImpactSpeed = FMath::Abs(FVector::DotProduct(GetVelocity(), Hit.ImpactNormal));
    float ImpactKmh = ImpactSpeed * 0.036f;

    if (ImpactKmh > 5.0f)
    {
        ACruiseSprintGameMode* GM = Cast<ACruiseSprintGameMode>(GetWorld()->GetAuthGameMode());
        if (GM)
        {
            GM->OnVehicleCollision(ImpactKmh);
        }
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] Vehicle collision at %.1f km/h with %s"),
            ImpactKmh, *OtherActor->GetName());
    }
}

void AChaosVehiclePawn::ApplyHellcatTune()
{
    // ONE published arcade preset (StraySpark Chaos Vehicles Masterclass 2026 illustrative
    // + native Chaos Arcade Control). Not inventing Hellcat-sim fidelity numbers.
    MaxSpeedKmh = 260.0f;
    ThrottleSensitivity = FMath::Max(ThrottleSensitivity, 1.25f);
    SteeringSensitivity = FMath::Max(SteeringSensitivity, 1.10f);
    if (auto* WheeledComp = Cast<UChaosWheeledVehicleMovementComponent>(GetVehicleMovementComponent()))
    {
        WheeledComp->EngineSetup.TorqueCurve.ExternalCurve = nullptr;
        // Muscle/arcade class: higher peak torque, auto gears, FinalRatio ~4.0 (StraySpark).
        WheeledComp->EngineSetup.MaxTorque = 700.0f;
        WheeledComp->EngineSetup.MaxRPM = 7000.0f;
        WheeledComp->EngineSetup.EngineIdleRPM = 900.0f;
        WheeledComp->EngineSetup.EngineBrakeEffect = 0.05f;
        FRichCurve* Curve = WheeledComp->EngineSetup.TorqueCurve.GetRichCurve();
        Curve->Reset();
        // Peak near ~70% MaxRPM (StraySpark guidance), punchy low-RPM for leave-grid.
        Curve->AddKey(0.0f, 420.0f);
        Curve->AddKey(1500.0f, 620.0f);
        Curve->AddKey(3500.0f, 700.0f);
        Curve->AddKey(5000.0f, 680.0f);
        Curve->AddKey(6000.0f, 520.0f);
        Curve->AddKey(7000.0f, 380.0f);
        WheeledComp->TransmissionSetup.bUseAutomaticGears = true;
        WheeledComp->TransmissionSetup.ForwardGearRatios = { 3.5f, 2.1f, 1.4f, 1.0f, 0.8f };
        WheeledComp->TransmissionSetup.ReverseGearRatios = { 3.0f };
        WheeledComp->TransmissionSetup.FinalRatio = 4.0f;
        WheeledComp->TransmissionSetup.ChangeUpRPM = 5950.0f; // ~85% MaxRPM
        WheeledComp->TransmissionSetup.ChangeDownRPM = 2800.0f; // ~40% MaxRPM
        WheeledComp->TransmissionSetup.GearChangeTime = 0.15f;
        // AWD rear-bias (sportier) — also avoids RWD+Undefined axle TorqueRatio=0 latch.
        WheeledComp->DifferentialSetup.DifferentialType = EVehicleDifferential::AllWheelDrive;
        WheeledComp->DifferentialSetup.FrontRearSplit = 0.35f;
        WheeledComp->EnableMechanicalSim(true);

        // Native Chaos Arcade Control (EnableSelfRighting + planted GTA/MC values).
        WheeledComp->bReverseAsBrake = true;
        WheeledComp->EnableSelfRighting(true);
        WheeledComp->StabilizeControl.Enabled = true;
        WheeledComp->StabilizeControl.AltitudeHoldZ = 12.0f;  // less balloon (forum + arcade)
        WheeledComp->StabilizeControl.PositionHoldXY = 2.5f; // lower = more forgiving slide
        WheeledComp->TorqueControl.Enabled = true;
        WheeledComp->TorqueControl.YawFromSteering = 0.40f;
        WheeledComp->TorqueControl.YawTorqueScaling = 0.30f;
        WheeledComp->TorqueControl.RotationDamping = 0.05f;
        WheeledComp->TargetRotationControl.Enabled = true;
        WheeledComp->TargetRotationControl.RotationStiffness = 0.45f;
        WheeledComp->TargetRotationControl.RotationDamping = 0.25f;
        WheeledComp->TargetRotationControl.AutoCentreRollStrength = 0.55f;
        WheeledComp->TargetRotationControl.AutoCentrePitchStrength = 0.40f;
        WheeledComp->TargetRotationControl.AutoCentreYawStrength = 0.15f;

        UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: StraySpark+ChaosArcade preset MaxTorque=700 AWD ReverseAsBrake pawn=%s"), *GetName());
    }
}


void AChaosVehiclePawn::ApplyChargerVisualMaterialFloor()
{
    // V17 visual floor: CARLA M_CarPaint_Master_New fails SM6 compile (missing Triplanar MF).
    // MI_DodgeCharger2024_BodyWork* instances that master -> DefaultMaterial hollow look.
    // Prefer M_NightCarPaint if present; else Engine BasicShapeMaterial (always compiles).
    UMaterialInterface* BodyMI = LoadObject<UMaterialInterface>(nullptr,
        TEXT("/Game/Materials/M_NightCarPaint.M_NightCarPaint"));
    if (!BodyMI)
    {
        BodyMI = LoadObject<UMaterialInterface>(nullptr,
            TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
        UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: V17 paint floor using BasicShapeMaterial (M_NightCarPaint missing; CARLA master broken)"));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: V17 paint floor using M_NightCarPaint"));
    }

    UMaterialInterface* GlassMI = LoadObject<UMaterialInterface>(nullptr,
        TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Materials/MI_GlassExt_Charger2024.MI_GlassExt_Charger2024"));
    if (!GlassMI)
    {
        GlassMI = LoadObject<UMaterialInterface>(nullptr,
            TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Materials/M_Glass_Vehicles.M_Glass_Vehicles"));
    }
    UMaterialInterface* LightsMI = LoadObject<UMaterialInterface>(nullptr,
        TEXT("/Game/Carla/Static/Car/4Wheeled/DodgeCharger2024/Materials/MI_VehicleLights_Charger2020.MI_VehicleLights_Charger2020"));

    auto TintBodyMID = [this](UPrimitiveComponent* Comp, int32 Slot, UMaterialInterface* Base)
    {
        if (!Comp || !Base) return;
        Comp->SetMaterial(Slot, Base);
        if (UMaterialInstanceDynamic* MID = Comp->CreateAndSetMaterialInstanceDynamic(Slot))
        {
            static const FName ColorParams[] = {
                TEXT("Base_color"), TEXT("Base_color_flakes"), TEXT("BaseColor"), TEXT("Base Color"),
                TEXT("Color"), TEXT("PaintColor"), TEXT("Tint"), TEXT("Albedo")
            };
            for (const FName& P : ColorParams)
            {
                MID->SetVectorParameterValue(P, BodyTint);
            }
            MID->SetScalarParameterValue(TEXT("Metallic"), 0.7f);
            MID->SetScalarParameterValue(TEXT("Roughness"), 0.25f);
            BoostNightPaintEmissive(MID, VehicleLook);
        }
    };

    if (USkeletalMeshComponent* Skel = GetMesh())
    {
        const int32 Num = Skel->GetNumMaterials();
        int32 BodySlots = 0;
        for (int32 i = 0; i < Num; ++i)
        {
            UMaterialInterface* Base = Skel->GetMaterial(i);
            const FString Name = Base ? Base->GetName() : FString();
            const bool bBody = Name.IsEmpty()
                || Name.Contains(TEXT("Body"))
                || Name.Contains(TEXT("Paint"))
                || Name.Contains(TEXT("CarPaint"))
                || Name.Contains(TEXT("DefaultMaterial"))
                || Name.Contains(TEXT("WorldGrid"));
            if (bBody || Num == 1)
            {
                TintBodyMID(Skel, i, BodyMI);
                ++BodySlots;
            }
        }
        UE_LOG(LogTemp, Warning, TEXT("raceGPS Cleveland: V17 paint floor bodySlots=%d bodyMI=%s pawn=%s"),
            BodySlots, BodyMI ? *BodyMI->GetName() : TEXT("null"), *GetName());
    }

    for (UStaticMeshComponent* Comp : CarlaDoorMeshes)
    {
        if (!Comp) continue;
        const FString CName = Comp->GetName();
        const int32 Num = Comp->GetNumMaterials();
        for (int32 i = 0; i < Num; ++i)
        {
            if (CName.Contains(TEXT("Glass")))
            {
                if (GlassMI) Comp->SetMaterial(i, GlassMI);
            }
            else if (CName.Contains(TEXT("Light")))
            {
                if (LightsMI) Comp->SetMaterial(i, LightsMI);
            }
            else
            {
                TintBodyMID(Comp, i, BodyMI);
            }
        }
    }
}


void AChaosVehiclePawn::ApplyVehicleLook(EVehicleLook Look)
{
    VehicleLook = Look;
    EnsureCarlaChargerMesh();
    EnsureCarlaChargerDoors();
    switch (Look)
    {
    case EVehicleLook::Hellcat:
        BodyTint = FLinearColor(1.00f, 0.42f, 0.08f, 1.0f); // V8 night-punch Go-Mango (not licensed)
        ApplyHellcatTune();
        break;
    case EVehicleLook::ChargerAsphalt:
        BodyTint = FLinearColor(0.12f, 0.13f, 0.15f, 1.0f); // V8 asphalt with night edge
        ApplyHellcatTune(); // same arcade powertrain as player for 3-car fun grid
        MaxSpeedKmh = 260.0f;
        break;
    case EVehicleLook::ChargerSilver:
        BodyTint = FLinearColor(0.85f, 0.87f, 0.90f, 1.0f); // V8 silver night read
        ApplyHellcatTune();
        MaxSpeedKmh = 250.0f;
        break;
    default:
        break;
    }

    USkeletalMeshComponent* Skel = GetMesh();
    if (!Skel)
    {
        return;
    }
    const int32 Mats = Skel->GetNumMaterials();
    for (int32 i = 0; i < Mats; ++i)
    {
        UMaterialInterface* Base = Skel->GetMaterial(i);
        if (!Base)
        {
            continue;
        }
        const FString Name = Base->GetName();
        const bool bBody = Name.Contains(TEXT("Body")) || Name.Contains(TEXT("Paint")) || Name.Contains(TEXT("CarPaint"));
        if (!bBody && Mats > 1)
        {
            continue;
        }
        // V10: CARLA master still missing Triplanar MF — swap body onto local night paint
        // so Base_color / flakes / emissive actually compile and read at night.
        if (UMaterialInterface* NightPaint = LoadObject<UMaterialInterface>(nullptr,
            TEXT("/Game/Materials/M_NightCarPaint.M_NightCarPaint")))
        {
            Skel->SetMaterial(i, NightPaint);
        }
        UMaterialInstanceDynamic* MID = Skel->CreateAndSetMaterialInstanceDynamic(i);
        if (!MID)
        {
            continue;
        }
        // Confirmed 2026-08-22 from MI_DodgeCharger2024_BodyWork + M_CarPaint_Master_New uassets.
        static const FName Params[] = {
            TEXT("Base_color"), TEXT("Base_color_flakes"), TEXT("BaseColor"), TEXT("Base Color"),
            TEXT("Color"), TEXT("PaintColor"), TEXT("Tint"), TEXT("Albedo"),
            TEXT("Dirt Color"), TEXT("Dirt Rim Color")
        };
        for (const FName& P : Params)
        {
            MID->SetVectorParameterValue(P, BodyTint);
        }
        // Clearcoat / metallic already exist as scalar setters on UMaterialInstanceDynamic.
        const bool bHellcatLook = (Look == EVehicleLook::Hellcat);
        const bool bSilverLook = (Look == EVehicleLook::ChargerSilver);
        const float Metallic = bSilverLook ? 0.92f : (bHellcatLook ? 0.78f : 0.55f);
        const float Roughness = bHellcatLook ? 0.18f : (bSilverLook ? 0.22f : 0.28f);
        const float ClearCoat = bHellcatLook ? 0.95f : (bSilverLook ? 0.85f : 0.70f);
        const float ClearCoatRough = bHellcatLook ? 0.08f : 0.12f;
        const float FlakesAmt = bHellcatLook ? 0.65f : (bSilverLook ? 0.45f : 0.15f);
        static const FName ScalarNames[] = {
            TEXT("Metallic"), TEXT("metallic"),
            TEXT("Roughness"), TEXT("roughness"),
            TEXT("ClearCoat"), TEXT("Clearcoat"), TEXT("Clear Coat"), TEXT("Coat"),
            TEXT("ClearCoatRoughness"), TEXT("ClearcoatRoughness"),
            TEXT("Flakes"), TEXT("FlakesAmount"), TEXT("flakes_amount")
        };
        const float ScalarValues[] = {
            Metallic, Metallic,
            Roughness, Roughness,
            ClearCoat, ClearCoat, ClearCoat, ClearCoat,
            ClearCoatRough, ClearCoatRough,
            FlakesAmt, FlakesAmt, FlakesAmt
        };
        for (int32 Si = 0; Si < UE_ARRAY_COUNT(ScalarNames); ++Si)
        {
            MID->SetScalarParameterValue(ScalarNames[Si], ScalarValues[Si]);
        }
        BoostNightPaintEmissive(MID, Look);
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] paint MID %s slot %d tint %s clearcoat %.2f metallic %.2f"),
            *Name, i, *BodyTint.ToString(), ClearCoat, Metallic);
    }
    ApplyChargerVisualMaterialFloor();
    EnsureShowcaseNightLights();
}

void AChaosVehiclePawn::BoostNightPaintEmissive(UMaterialInstanceDynamic* MID, EVehicleLook Look) const
{
    if (!MID)
    {
        return;
    }
    // V11: body paint is lit clearcoat (BaseColor + Metallic/Roughness/Specular), NOT emissive neon.
    // Headlights/taillights stay on via EnsureShowcaseNightLights point lights.
    (void)Look;
    const FLinearColor Emissive = FLinearColor::Black;
    static const FName ENames[] = {
        TEXT("EmissiveColor"), TEXT("Emissive"), TEXT("EmissiveColor2"),
        TEXT("Base_color_emissive"), TEXT("CoatEmissive")
    };
    for (const FName& N : ENames)
    {
        MID->SetVectorParameterValue(N, Emissive);
    }
    MID->SetScalarParameterValue(TEXT("EmissiveStrength"), 0.f);
    MID->SetScalarParameterValue(TEXT("EmissiveIntensity"), 0.f);
    MID->SetScalarParameterValue(TEXT("EmissiveMultiplier"), 0.f);
    MID->SetScalarParameterValue(TEXT("Specular"), 0.85f);
}

void AChaosVehiclePawn::EnsureShowcaseNightLights()
{
    USkeletalMeshComponent* Skel = GetMesh();
    if (!Skel)
    {
        return;
    }
    auto MakeLight = [&](TObjectPtr<UPointLightComponent>& Slot, const TCHAR* Name, const FVector& Rel, const FLinearColor& Color, float Intensity, float Radius)
    {
        if (!Slot)
        {
            Slot = NewObject<UPointLightComponent>(this, Name);
            Slot->SetupAttachment(Skel);
            Slot->RegisterComponent();
            Slot->SetMobility(EComponentMobility::Movable);
            Slot->SetCastShadows(false);
        }
        Slot->SetRelativeLocation(Rel);
        Slot->SetLightColor(Color);
        Slot->SetIntensity(Intensity);
        Slot->SetAttenuationRadius(Radius);
        Slot->SetVisibility(true);
    };
    // Approx Charger lamp positions (cm).
    // V16: 28000 lm / 42 m radius per headlight (x3 cars) painted the ground plane
    // solid white. Physical-scale values: visible pools, no blowout.
    MakeLight(HeadlightL, TEXT("HeadlightL"), FVector(210.f, -70.f, 55.f), FLinearColor(1.0f, 0.96f, 0.85f), 700.f, 600.f); // visual floor 2026-09-24: was 4500/2400 void blowout
    MakeLight(HeadlightR, TEXT("HeadlightR"), FVector(210.f,  70.f, 55.f), FLinearColor(1.0f, 0.96f, 0.85f), 700.f, 600.f);
    MakeLight(TaillightL, TEXT("TaillightL"), FVector(-210.f, -70.f, 60.f), FLinearColor(1.0f, 0.08f, 0.05f), 350.f, 400.f);
    MakeLight(TaillightR, TEXT("TaillightR"), FVector(-210.f,  70.f, 60.f), FLinearColor(1.0f, 0.08f, 0.05f), 350.f, 400.f);
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] showcase night lights on look=%d"), static_cast<int32>(VehicleLook));
}




