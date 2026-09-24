#include "ClevelandLookDirector.h"
#include "DayNightCycle.h"
#include "PostProcessController.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/DirectionalLight.h"
#include "Engine/ReflectionCapture.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"

AClevelandLookDirector::AClevelandLookDirector()
{
	PrimaryActorTick.bCanEverTick = false;
	Mode = EClevelandVisualMode::Sunset;
}

void AClevelandLookDirector::BeginPlay()
{
	Super::BeginPlay();
	ApplyVisualMode(Mode);
}

bool AClevelandLookDirector::TryParsePresetName(const FString& Name, EClevelandVisualMode& OutMode)
{
	const FString N = Name.TrimStartAndEnd().ToLower();
	if (N == TEXT("sunset"))
	{
		OutMode = EClevelandVisualMode::Sunset;
		return true;
	}
	if (N == TEXT("twilight"))
	{
		OutMode = EClevelandVisualMode::Twilight;
		return true;
	}
	if (N == TEXT("midnight") || N == TEXT("midnightrun"))
	{
		OutMode = EClevelandVisualMode::Midnight;
		return true;
	}
	return false;
}

FString AClevelandLookDirector::PresetDisplayName(EClevelandVisualMode InMode)
{
	switch (InMode)
	{
	case EClevelandVisualMode::Sunset: return TEXT("Sunset");
	case EClevelandVisualMode::Twilight: return TEXT("Twilight");
	case EClevelandVisualMode::Midnight: return TEXT("Midnight");
	default: return TEXT("Unknown");
	}
}

void AClevelandLookDirector::EnsureCycleAndPost()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	Cycle = Cast<ADayNightCycle>(UGameplayStatics::GetActorOfClass(World, ADayNightCycle::StaticClass()));
	if (!Cycle)
	{
		Cycle = World->SpawnActor<ADayNightCycle>(ADayNightCycle::StaticClass());
	}
	Post = Cast<APostProcessController>(UGameplayStatics::GetActorOfClass(World, APostProcessController::StaticClass()));
	if (!Post)
	{
		Post = World->SpawnActor<APostProcessController>(APostProcessController::StaticClass());
	}
}

void AClevelandLookDirector::SuppressCompetingLights() const
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	int32 DisabledDir = 0;
	TArray<AActor*> DirLights;
	UGameplayStatics::GetAllActorsOfClass(World, ADirectionalLight::StaticClass(), DirLights);
	for (AActor* LightActor : DirLights)
	{
		if (!LightActor)
		{
			continue;
		}
		TArray<UDirectionalLightComponent*> Comps;
		LightActor->GetComponents<UDirectionalLightComponent>(Comps);
		for (UDirectionalLightComponent* Comp : Comps)
		{
			if (!Comp)
			{
				continue;
			}
			if (Cycle && Comp == Cycle->SunLight)
			{
				continue;
			}
			Comp->SetVisibility(false);
			Comp->SetIntensity(0.f);
			++DisabledDir;
		}
	}

	int32 DisabledCaptures = 0;
	TArray<AActor*> Captures;
	UGameplayStatics::GetAllActorsOfClass(World, AReflectionCapture::StaticClass(), Captures);
	for (AActor* Capture : Captures)
	{
		if (!Capture)
		{
			continue;
		}
		Capture->SetActorHiddenInGame(true);
		Capture->SetActorEnableCollision(false);
		++DisabledCaptures;
	}

	UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] look: suppressed extra directional lights=%d reflection captures=%d"),
		DisabledDir, DisabledCaptures);
}

void AClevelandLookDirector::ApplyEpicConsoleVars() const
{
	if (!GEngine)
	{
		return;
	}
	UWorld* World = GetWorld();
	GEngine->Exec(World, TEXT("DisableAllScreenMessages"));
	GEngine->Exec(World, TEXT("r.SkyAtmosphere 1"));
	GEngine->Exec(World, TEXT("r.ShadowQuality 5"));
	GEngine->Exec(World, TEXT("r.BloomQuality 5"));
	GEngine->Exec(World, TEXT("r.ReflectionMethod 1"));
	GEngine->Exec(World, TEXT("r.DynamicGlobalIlluminationMethod 1"));
	GEngine->Exec(World, TEXT("r.Tonemapper.Quality 5"));
	GEngine->Exec(World, TEXT("r.DefaultFeature.Bloom 1"));
	GEngine->Exec(World, TEXT("r.DefaultFeature.AutoExposure 1"));
	GEngine->Exec(World, TEXT("r.EyeAdaptationQuality 2"));
}

void AClevelandLookDirector::ApplyVisualMode(EClevelandVisualMode InMode)
{
	Mode = InMode;
	EnsureCycleAndPost();
	ApplyEpicConsoleVars();
	SuppressCompetingLights();
	switch (Mode)
	{
	case EClevelandVisualMode::Sunset:
		ApplySunset();
		break;
	case EClevelandVisualMode::Twilight:
		ApplyTwilight();
		break;
	case EClevelandVisualMode::Midnight:
	default:
		ApplyMidnight();
		break;
	}
	LogFinalLook(*PresetDisplayName(Mode));
}

void AClevelandLookDirector::ApplySunset()
{
	// Declared: 18:45 local. DayNightCycle geometric sunset ~18:00 (Pitch~0, Yaw~270 west).
	// 18:45 => SunAngle≈191.25, Pitch≈+15.6 (model), Yaw≈281.25 — low western sun, warm grade.
	if (Cycle)
	{
		Cycle->bMoonAtNight = false;
		Cycle->bPaused = true;
		Cycle->bUseSkyAtmosphere = true;
		Cycle->bUseVolumetricClouds = true;
		Cycle->SetTimeOfDay(18.75f);
		if (Cycle->SunLight)
		{
			Cycle->SunLight->SetIntensity(2.10f);
			Cycle->SunLight->SetLightColor(FLinearColor(1.0f, 0.62f, 0.32f));
			Cycle->SunLight->SetVisibility(true);
		}
		if (Cycle->SkyLight)
		{
			Cycle->SkyLight->SetIntensity(1.05f);
			Cycle->SkyLight->SetLightColor(FLinearColor(1.0f, 0.78f, 0.55f));
		}
	}
	if (Post)
	{
		Post->EpicPreset.BloomIntensity = 1.85f;
		Post->EpicPreset.BloomThreshold = 0.70f;
		Post->EpicPreset.Contrast = 1.14f;
		Post->EpicPreset.Saturation = 1.22f;
		Post->EpicPreset.ChromaticAberrationIntensity = 0.05f;
		Post->EpicPreset.VignetteIntensity = 0.30f;
		Post->EpicPreset.SceneColorTintR = 1.12f;
		Post->EpicPreset.SceneColorTintG = 0.95f;
		Post->EpicPreset.SceneColorTintB = 0.82f;
		Post->EpicPreset.AutoExposureBias = 0.05f;
		Post->ApplyPresetForTier(EVisualQualityTier::Epic);
	}
	if (GEngine)
	{
		GEngine->Exec(GetWorld(), TEXT("r.VolumetricCloud 1"));
	}
	UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] Sunset applied (18:45 warm western sun, dry surface unchanged)"));
}

void AClevelandLookDirector::ApplyTwilight()
{
	// Declared: 20:00 local. SunAngle=210, Pitch≈+40 model / below practical horizon feel, cool blue hour.
	if (Cycle)
	{
		Cycle->bMoonAtNight = true;
		Cycle->NightMoonIntensity = 1.55f;
		Cycle->bPaused = true;
		Cycle->bUseSkyAtmosphere = true;
		Cycle->bUseVolumetricClouds = false;
		Cycle->SetTimeOfDay(20.0f);
		if (Cycle->SunLight)
		{
			Cycle->SunLight->SetIntensity(1.70f);
			Cycle->SunLight->SetLightColor(FLinearColor(0.72f, 0.78f, 1.0f));
			Cycle->SunLight->SetVisibility(true);
		}
		if (Cycle->SkyLight)
		{
			Cycle->SkyLight->SetIntensity(1.60f);
			Cycle->SkyLight->SetLightColor(FLinearColor(0.55f, 0.62f, 0.88f));
		}
	}
	if (Post)
	{
		Post->EpicPreset.BloomIntensity = 0.90f;
		Post->EpicPreset.BloomThreshold = 0.95f;
		Post->EpicPreset.Contrast = 1.10f;
		Post->EpicPreset.Saturation = 1.10f;
		Post->EpicPreset.ChromaticAberrationIntensity = 0.05f;
		Post->EpicPreset.VignetteIntensity = 0.34f;
		Post->EpicPreset.SceneColorTintR = 0.92f;
		Post->EpicPreset.SceneColorTintG = 0.95f;
		Post->EpicPreset.SceneColorTintB = 1.08f;
		Post->EpicPreset.AutoExposureBias = 0.55f;
		Post->ApplyPresetForTier(EVisualQualityTier::Epic);
	}
	if (GEngine)
	{
		GEngine->Exec(GetWorld(), TEXT("r.VolumetricCloud 0"));
	}
	UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] Twilight applied (20:00 blue hour, dry surface unchanged)"));
}

void AClevelandLookDirector::ApplyMidnight()
{
	// Declared: 22:00 local. Moon directional (bMoonAtNight) — matches showcase MidnightRun hour.
	if (Cycle)
	{
		Cycle->bMoonAtNight = true;
		Cycle->NightMoonIntensity = 2.35f;
		Cycle->bPaused = true;
		Cycle->bUseSkyAtmosphere = true;
		Cycle->bUseVolumetricClouds = false;
		Cycle->SetTimeOfDay(22.0f);
		if (Cycle->SunLight)
		{
			Cycle->SunLight->SetIntensity(2.40f);
			Cycle->SunLight->SetLightColor(FLinearColor(0.82f, 0.86f, 1.0f));
			Cycle->SunLight->SetVisibility(true);
		}
		if (Cycle->SkyLight)
		{
			Cycle->SkyLight->SetIntensity(2.20f);
			Cycle->SkyLight->SetLightColor(FLinearColor(0.70f, 0.74f, 0.86f));
			Cycle->SkyLight->RecaptureSky();
		}
	}
	if (Post)
	{
		Post->EpicPreset.BloomIntensity = 0.55f;
		Post->EpicPreset.BloomThreshold = 1.10f;
		Post->EpicPreset.Contrast = 1.12f;
		Post->EpicPreset.Saturation = 1.18f;
		Post->EpicPreset.ChromaticAberrationIntensity = 0.06f;
		Post->EpicPreset.VignetteIntensity = 0.28f;
		Post->EpicPreset.SceneColorTintR = 1.02f;
		Post->EpicPreset.SceneColorTintG = 0.98f;
		Post->EpicPreset.SceneColorTintB = 0.96f;
		Post->EpicPreset.AutoExposureBias = 1.15f;
		Post->ApplyPresetForTier(EVisualQualityTier::Epic);
	}
	if (GEngine)
	{
		GEngine->Exec(GetWorld(), TEXT("r.VolumetricCloud 0"));
	}
	UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] Midnight applied (22:00 moon directional, dry surface unchanged)"));
}

void AClevelandLookDirector::LogFinalLook(const TCHAR* Tag) const
{
	const float Hour = Cycle ? Cycle->GetTimeOfDay() : -1.f;
	float SunI = -1.f;
	float SkyI = -1.f;
	FRotator SunR = FRotator::ZeroRotator;
	if (Cycle && Cycle->SunLight)
	{
		SunI = Cycle->SunLight->Intensity;
		SunR = Cycle->SunLight->GetComponentRotation();
	}
	if (Cycle && Cycle->SkyLight)
	{
		SkyI = Cycle->SkyLight->Intensity;
	}
	UE_LOG(LogTemp, Log,
		TEXT("[raceGPS Cleveland] look FINAL [%s]: hour=%.2f sunI=%.2f sunPitch=%.1f sunYaw=%.1f skyI=%.2f (Frame A X=east Y=north)"),
		Tag, Hour, SunI, SunR.Pitch, SunR.Yaw, SkyI);
}
