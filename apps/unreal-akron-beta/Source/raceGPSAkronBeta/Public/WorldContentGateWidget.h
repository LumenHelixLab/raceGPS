// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "PreflightSystem.h"
#include "WorldContentGateWidget.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnWorldContentGateDismissed);

UCLASS()
class RACEGPSAKRONBETA_API UWorldContentGateWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    void RefreshFromPreflight();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    void OnVerifyInstallationClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    void OnOpenDocsClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    void OnReinstallClicked();

    UFUNCTION(BlueprintCallable, Category = "raceGPS|WorldContent")
    void OnQuitClicked();

    UFUNCTION(BlueprintPure, Category = "raceGPS|WorldContent")
    FString GetStatusText() const { return StatusMessage; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|WorldContent")
    FString GetRecommendedActionText() const { return RecommendedAction; }

    UFUNCTION(BlueprintPure, Category = "raceGPS|WorldContent")
    bool IsWorldReady() const { return bWorldReady; }

    UPROPERTY(BlueprintAssignable, Category = "raceGPS|WorldContent")
    FOnWorldContentGateDismissed OnDismissed;

    UPROPERTY(meta = (BindWidgetOptional))
    class UTextBlock* TitleText;

    UPROPERTY(meta = (BindWidgetOptional))
    class UTextBlock* StatusTextBlock;

    UPROPERTY(meta = (BindWidgetOptional))
    class UTextBlock* ActionTextBlock;

    UPROPERTY(meta = (BindWidgetOptional))
    class UButton* VerifyButton;

    UPROPERTY(meta = (BindWidgetOptional))
    class UButton* DocsButton;

    UPROPERTY(meta = (BindWidgetOptional))
    class UButton* ReinstallButton;

    UPROPERTY(meta = (BindWidgetOptional))
    class UButton* QuitButton;

protected:
    void BindButtons();
    void UpdateDisplay();
    void DismissIfReady();

    FString StatusMessage;
    FString RecommendedAction;
    bool bWorldReady = false;
};