// Copyright raceGPS. All Rights Reserved.

#include "WorldContentGateWidget.h"
#include "WorldContentInstaller.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Kismet/GameplayStatics.h"
#include "Kismet/KismetSystemLibrary.h"
#include "HAL/PlatformProcess.h"

void UWorldContentGateWidget::NativeConstruct()
{
    Super::NativeConstruct();
    BindButtons();
    RefreshFromPreflight();
}

void UWorldContentGateWidget::BindButtons()
{
    if (VerifyButton)
    {
        VerifyButton->OnClicked.AddDynamic(this, &UWorldContentGateWidget::OnVerifyInstallationClicked);
    }
    if (DocsButton)
    {
        DocsButton->OnClicked.AddDynamic(this, &UWorldContentGateWidget::OnOpenDocsClicked);
    }
    if (ReinstallButton)
    {
        ReinstallButton->OnClicked.AddDynamic(this, &UWorldContentGateWidget::OnReinstallClicked);
    }
    if (QuitButton)
    {
        QuitButton->OnClicked.AddDynamic(this, &UWorldContentGateWidget::OnQuitClicked);
    }
}

void UWorldContentGateWidget::RefreshFromPreflight()
{
    const FPreflightCheck WorldCheck = UPreflightSystem::CheckWorldMap();
    bWorldReady = WorldCheck.Status == EPreflightStatus::Pass;
    StatusMessage = WorldCheck.Detail;
    RecommendedAction = WorldCheck.RecommendedAction;
    if (RecommendedAction.IsEmpty() && !bWorldReady)
    {
        RecommendedAction = TEXT("Verify installation, reinstall from Releases, or follow the setup guide.");
    }
    UpdateDisplay();
    DismissIfReady();
}

void UWorldContentGateWidget::UpdateDisplay()
{
    if (TitleText)
    {
        TitleText->SetText(FText::FromString(
            bWorldReady ? TEXT("Akron world ready") : TEXT("Akron world not installed")));
    }
    if (StatusTextBlock)
    {
        StatusTextBlock->SetText(FText::FromString(StatusMessage));
    }
    if (ActionTextBlock)
    {
        ActionTextBlock->SetText(FText::FromString(RecommendedAction));
    }
}

void UWorldContentGateWidget::DismissIfReady()
{
    if (bWorldReady)
    {
        OnDismissed.Broadcast();
        RemoveFromParent();
    }
}

void UWorldContentGateWidget::OnVerifyInstallationClicked()
{
    FString Summary;
    UWorldContentInstaller::VerifyInstallation(Summary);
    UE_LOG(LogTemp, Log, TEXT("[raceGPS] Installation verify:\n%s"), *Summary);
    RefreshFromPreflight();
}

void UWorldContentGateWidget::OnOpenDocsClicked()
{
    FPlatformProcess::LaunchURL(*UWorldContentInstaller::GetSetupGuideUrl(), nullptr, nullptr);
}

void UWorldContentGateWidget::OnReinstallClicked()
{
    FPlatformProcess::LaunchURL(*UWorldContentInstaller::GetReleasesUrl(), nullptr, nullptr);
}

void UWorldContentGateWidget::OnQuitClicked()
{
    UKismetSystemLibrary::QuitGame(GetWorld(), GetOwningPlayer(), EQuitPreference::Quit, true);
}