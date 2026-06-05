#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "NeonHUD.generated.h"

UCLASS()
class RACEGPSAKRONBETA_API ANeonHUD : public AHUD
{
    GENERATED_BODY()

public:
    ANeonHUD(const FObjectInitializer& ObjectInitializer);

    virtual void DrawHUD() override;
    virtual void BeginPlay() override;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void SetRaceTime(float Seconds);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void SetCheckpointProgress(int32 Current, int32 Total);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void SetSpeedKmh(float Speed);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void SetTelemetry(float RPM, int32 Gear);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void SetCountdownValue(int32 Value);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void ShowCountdown(bool bVisible);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|HUD")
    void ShowRaceFinished(float FinalTime, const FString& Medal);

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    UFont* MainFont;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    UFont* LargeFont;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    FLinearColor NeonCyan = FLinearColor(0.0f, 0.9f, 1.0f);

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    FLinearColor NeonMagenta = FLinearColor(1.0f, 0.0f, 0.8f);

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    FLinearColor NeonGreen = FLinearColor(0.0f, 1.0f, 0.4f);

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    FLinearColor NeonYellow = FLinearColor(1.0f, 0.9f, 0.0f);

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|HUD")
    FLinearColor DarkBackground = FLinearColor(0.02f, 0.02f, 0.05f, 0.85f);

protected:
    float RaceTime = 0.0f;
    int32 CurrentCheckpoint = 0;
    int32 TotalCheckpoints = 0;
    float SpeedKmh = 0.0f;
    float EngineRPM = 0.0f;
    int32 CurrentGear = 0;
    int32 CountdownValue = 0;
    bool bShowCountdown = false;
    bool bShowFinished = false;
    FString FinishedMedal;
    float FinishedTime = 0.0f;

    void DrawRaceInfo();
    void DrawCountdown();
    void DrawFinishedScreen();
    void DrawNeonPanel(float X, float Y, float Width, float Height, const FLinearColor& BorderColor);
    FString FormatTime(float Seconds) const;
};
