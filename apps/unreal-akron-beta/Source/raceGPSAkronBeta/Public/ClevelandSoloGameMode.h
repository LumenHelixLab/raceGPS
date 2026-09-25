#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "ClevelandLookDirector.h"
#include "ClevelandSoloGameMode.generated.h"

class AClevelandLookDirector;
class AChaosVehiclePawn;

/**
 * G4 solo Cleveland drive path. Loads Cleveland5_0KmWorld with optional Burke
 * start teleport + Sunset/Twilight/Midnight look. Does NOT change
 * GlobalDefaultGameMode (CruiseSprint remains the ini default).
 *
 * Launch: apps/unreal-akron-beta/LaunchCleveland.bat [Sunset|Twilight|Midnight]
 * Cmdline: -ClevelandPreset=Sunset  (also accepts -ClevelandSkipIntro)
 *
 * Full ClevelandShowcaseGameMode / RaceGridManager / AI stack is NOT required
 * for G4 solo proof and remains a G5 concern.
 */
UCLASS()
class RACEGPSAKRONBETA_API AClevelandSoloGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AClevelandSoloGameMode();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "raceGPS|Cleveland")
	FString ProductTitle = TEXT("raceGPS");

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "raceGPS|Cleveland")
	FString CircuitTitle = TEXT("Cleveland Historic Circuit");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Cleveland")
	FString CityPackRelativeDir = TEXT("citypacks/cleveland/burke_gp_1997");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Cleveland|Look")
	EClevelandVisualMode VisualPreset = EClevelandVisualMode::Sunset;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "raceGPS|Cleveland|Look")
	TObjectPtr<AClevelandLookDirector> LookDirector;

	/** Height above geo plane for spawn (cm). Burke field ~ flat. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|Cleveland")
	float SpawnHeightCm = 80.f;

	UFUNCTION(Exec)
	void ClevelandPreset(const FString& Name);

	UFUNCTION(Exec)
	void ClevelandCaptureStill(const FString& Label);

protected:
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	void ResolvePresetFromCommandLine();
	void SpawnLookDirector();
	bool TryTeleportPlayerToBurkeStart();
	FString ResolveCityPackFile(const FString& FileName) const;
	void CaptureHighResStill(const FString& Phase);
	void LogSoloReady();

	bool bTeleported = false;
	bool bLoggedReady = false;
	float ReadyElapsed = 0.f;
	bool bCapturePending = false;
	float CaptureDelay = 5.0f;
	float CaptureElapsed = 0.f;
	FString PendingCaptureLabel;
};
