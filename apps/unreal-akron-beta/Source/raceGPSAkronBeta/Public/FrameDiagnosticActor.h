#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FrameDiagnosticActor.generated.h"

/**
 * Editor/runtime diagnostic for SOURCE_TO_UNREAL_FRAME_v1.
 * Place in a level (or spawn via console) to verify:
 * - 100 m east/north/up marker arms (10000 uu)
 * - 7 m-wide road ribbon half-width 350 uu
 *
 * How to place:
 * 1. Open any map in raceGPSAkronBetaEditor
 * 2. Place Actor -> FrameDiagnosticActor (or: `ke * FrameDiagnosticActor`)
 * 3. Call DrawDiagnostic / enable bAutoDrawOnBeginPlay
 * 4. Measure arms with editor ruler; expect 10000 uu (+/-1) and road width 700 uu (+/-1)
 */
UCLASS()
class RACEGPSAKRONBETA_API AFrameDiagnosticActor : public AActor
{
    GENERATED_BODY()

public:
    AFrameDiagnosticActor();

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|FrameDiag")
    bool bAutoDrawOnBeginPlay = true;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|FrameDiag")
    float LineLengthMeters = 100.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|FrameDiag")
    float RoadWidthMeters = 7.0f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|FrameDiag")
    float OriginLat = 41.51722f;

    UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "raceGPS|FrameDiag")
    float OriginLon = -81.68306f;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|FrameDiag")
    void DrawDiagnostic();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|FrameDiag")
    bool SelfCheck(float& OutEastLenCm, float& OutNorthLenCm, float& OutUpLenCm, float& OutRoadWidthCm) const;

protected:
    virtual void BeginPlay() override;
};
