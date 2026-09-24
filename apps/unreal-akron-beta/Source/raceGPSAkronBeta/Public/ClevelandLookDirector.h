#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ClevelandLookDirector.generated.h"

/**
 * G4 visual presets for Cleveland Historic Circuit (provisional Burke pack).
 * Exact names required by gate: Sunset / Twilight / Midnight.
 * Same dry-surface physics/geometry; only lighting/grade change.
 * Does not change GlobalDefaultGameMode (CruiseSprint stays default).
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

	UPROPERTY()
	TObjectPtr<class ADayNightCycle> Cycle;

	UPROPERTY()
	TObjectPtr<class APostProcessController> Post;
};
