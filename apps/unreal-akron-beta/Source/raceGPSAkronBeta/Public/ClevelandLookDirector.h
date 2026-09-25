#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PointLight.h"
#include "ClevelandLookDirector.generated.h"

/**
 * G4 visual presets for Cleveland Historic Circuit (provisional Burke pack).
 * Exact names required by gate: Sunset / Twilight / Midnight.
 * Same dry-surface physics/geometry; only lighting/grade change.
 * Does not change GlobalDefaultGameMode (CruiseSprint stays default).
 * Midnight carries the V15 Midnight-Club night toolbox (fog, lamps, wet apron, city glow).
 */
UENUM(BlueprintType)
enum class EClevelandVisualMode : uint8
{
	Sunset UMETA(DisplayName = "Sunset"),
	Twilight UMETA(DisplayName = "Twilight"),
	Midnight UMETA(DisplayName = "Midnight")
};

/**
 * Applies declared solar orientation via ADayNightCycle (Frame A: X=east Y=north).
 * DayNightCycle model: SunAngle=(hour/24-0.25)*360; Pitch=-sin(SunAngle)*80; Yaw=SunAngle+90.
 * Geometric sunset in that model is ~18:00 (Pitch~0, Yaw~270 = west).
 */
UCLASS()
class RACEGPSAKRONBETA_API AClevelandLookDirector : public AActor
{
	GENERATED_BODY()

public:
	AClevelandLookDirector();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Cleveland|Look")
	EClevelandVisualMode Mode = EClevelandVisualMode::Sunset;

	UFUNCTION(BlueprintCallable, Category = "raceGPS|Cleveland|Look")
	void ApplyVisualMode(EClevelandVisualMode InMode);

	UFUNCTION(BlueprintCallable, Category = "raceGPS|Cleveland|Look")
	static bool TryParsePresetName(const FString& Name, EClevelandVisualMode& OutMode);

	UFUNCTION(BlueprintPure, Category = "raceGPS|Cleveland|Look")
	static FString PresetDisplayName(EClevelandVisualMode InMode);

protected:
	virtual void BeginPlay() override;

	void EnsureCycleAndPost();
	void SuppressCompetingLights() const;
	void ApplyEpicConsoleVars() const;
	void ApplySunset();
	void ApplyTwilight();
	void ApplyMidnight();
	void LogFinalLook(const TCHAR* Tag) const;

	// V15 night toolbox (invoked by ApplyMidnight / ApplyVisualMode failsafe).
	void ApplyLookToEnvironment() const;
	void EnsureLightingFailsafe() const;
	void EnsureNightFogAndLamps();
	void ApplyNightSkyFix() const;
	void ApplyNightCityHISMGlow() const;
	void ApplyNightGroundWetness() const;
	void HideSprawlBuildingHISM();
	void QuietCesiumTilesets() const;
	void EnsureBurkeWetApron();

	UPROPERTY()
	TObjectPtr<class ADayNightCycle> Cycle;

	UPROPERTY()
	TObjectPtr<class APostProcessController> Post;

	UPROPERTY()
	TObjectPtr<class AExponentialHeightFog> NightFog;

	UPROPERTY()
	TArray<TObjectPtr<class APointLight>> NightLamps;

	/** Runtime-only wet apron under Burke. Not saved. */
	UPROPERTY()
	TObjectPtr<class AStaticMeshActor> BurkeWetApron;

	/** Runtime-only south downtown HISM band. Original T10 HISMs stay on disk, hidden. */
	UPROPERTY()
	TObjectPtr<AActor> DowntownBandActor;

	bool bSprawlHidden = false;
};
