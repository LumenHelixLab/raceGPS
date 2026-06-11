#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "VehicleTuningData.h"
#include "MainMenuWidget.generated.h"

UCLASS()
class RACEGPSAKRONBETA_API UMainMenuWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void OnPlayClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void OnSettingsClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void OnQuitClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Menu")
    void OnSelectRouteClicked(const FString& RouteId);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|LAN")
    void OnHostLANClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|LAN")
    void OnJoinLANClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Vehicle")
    UVehicleTuningData* GetSelectedVehicle() const;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Vehicle")
    FString GetSelectedHandlingMode() const;

    UFUNCTION()
    void UpdateVehicleInfo();

    UFUNCTION()
    void OnVehicleSelectionChanged(FString SelectedItem, ESelectInfo::Type SelectionType);

    UFUNCTION()
    void OnRouteSelectionChanged(FString SelectedItem, ESelectInfo::Type SelectionType);

    UFUNCTION()
    void OnHandlingSelectionChanged(FString SelectedItem, ESelectInfo::Type SelectionType);

    UFUNCTION(BlueprintPure, Category = "raceGPS|UX")
    FString BuildDriveSummaryText() const;

    UFUNCTION(BlueprintPure, Category = "raceGPS|UX")
    FString BuildLaunchButtonText() const;

    UFUNCTION(BlueprintPure, Category = "raceGPS|UX")
    FString BuildVersionLine() const;

    UFUNCTION(BlueprintPure, Category = "raceGPS|UX")
    FString BuildVehicleClassLabel(const UVehicleTuningData* Vehicle) const;

    UPROPERTY(meta = (BindWidget))
    class UButton* PlayButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* SettingsButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* QuitButton;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* TitleText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* VersionText;

    UPROPERTY(meta = (BindWidget))
    class UComboBoxString* RouteSelector;

    UPROPERTY(meta = (BindWidget))
    class UComboBoxString* VehicleSelector;

    UPROPERTY(meta = (BindWidget))
    class UComboBoxString* HandlingSelector;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* VehicleInfoText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* HandlingInfoText;

    UPROPERTY(meta = (BindWidget))
    class UButton* HostLANButton;

    UPROPERTY(meta = (BindWidget))
    class UButton* JoinLANButton;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Menu")
    FString GameLevelName = TEXT("AkronWorld");

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Menu")
    TArray<FString> AvailableRoutes;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Menu")
    TArray<TObjectPtr<UVehicleTuningData>> AvailableVehicles;

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Menu")
    TArray<FString> AvailableHandlingModes = { TEXT("Arcade"), TEXT("Drift"), TEXT("Simulation") };

    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|LAN")
    TSubclassOf<class ULANBrowserWidget> LANBrowserClass;
};
