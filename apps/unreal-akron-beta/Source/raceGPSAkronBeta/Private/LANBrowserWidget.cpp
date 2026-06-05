#include "LANBrowserWidget.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Components/ListView.h"
#include "Components/Slider.h"
#include "LANSessionManager.h"

void ULANBrowserWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (HostButton)
    {
        HostButton->OnClicked.AddDynamic(this, &ULANBrowserWidget::OnHostClicked);
    }
    if (JoinButton)
    {
        JoinButton->OnClicked.AddDynamic(this, &ULANBrowserWidget::OnJoinClicked);
    }
    if (RefreshButton)
    {
        RefreshButton->OnClicked.AddDynamic(this, &ULANBrowserWidget::OnRefreshClicked);
    }
    if (BackButton)
    {
        BackButton->OnClicked.AddDynamic(this, &ULANBrowserWidget::OnBackClicked);
    }
    if (MaxPlayersSlider)
    {
        MaxPlayersSlider->OnValueChanged.AddDynamic(this, &ULANBrowserWidget::UpdateMaxPlayersDisplay);
        MaxPlayersSlider->SetValue(4.0f);
    }

    // Create LAN manager
    LANManager = NewObject<ULANSessionManager>(this);
    if (LANManager)
    {
        LANManager->OnSessionsFound.AddDynamic(this, &ULANBrowserWidget::OnSessionsFound);
        LANManager->OnSessionJoined.AddDynamic(this, &ULANBrowserWidget::OnJoinComplete);
        LANManager->OnSessionCreated.AddDynamic(this, &ULANBrowserWidget::OnHostComplete);
    }

    UpdateMaxPlayersDisplay();

    if (StatusText)
    {
        StatusText->SetText(FText::FromString(TEXT("Click Refresh to find LAN sessions")));
    }
}

void ULANBrowserWidget::OnHostClicked()
{
    if (!LANManager)
        return;

    int32 MaxPlayers = MaxPlayersSlider ? FMath::RoundToInt(MaxPlayersSlider->GetValue()) : 4;
    if (StatusText)
    {
        StatusText->SetText(FText::FromString(TEXT("Creating LAN session...")));
    }
    LANManager->HostSession(MaxPlayers);
}

void ULANBrowserWidget::OnJoinClicked()
{
    if (!LANManager || SelectedSessionIndex < 0 || SelectedSessionIndex >= FoundSessions.Num())
        return;

    if (StatusText)
    {
        StatusText->SetText(FText::FromString(TEXT("Joining session...")));
    }
    LANManager->JoinSession(FoundSessions[SelectedSessionIndex]);
}

void ULANBrowserWidget::OnRefreshClicked()
{
    if (!LANManager)
        return;

    FoundSessions.Empty();
    SelectedSessionIndex = -1;

    if (StatusText)
    {
        StatusText->SetText(FText::FromString(TEXT("Searching for LAN sessions...")));
    }
    LANManager->FindSessions();
}

void ULANBrowserWidget::OnSessionSelected(int32 Index)
{
    SelectedSessionIndex = Index;
    if (StatusText && Index >= 0 && Index < FoundSessions.Num())
    {
        const FOnlineSessionSearchResult& Result = FoundSessions[Index].OnlineResult;
        FString SessionName = TEXT("Unknown");
        Result.Session.SessionSettings.Get(FName(TEXT("SESSIONNAME")), SessionName);
        FString Ping = FString::Printf(TEXT("%dms"), Result.PingInMs);
        StatusText->SetText(FText::FromString(FString::Printf(TEXT("Selected: %s (Ping: %s)"), *SessionName, *Ping)));
    }
}

void ULANBrowserWidget::OnBackClicked()
{
    RemoveFromParent();
}

void ULANBrowserWidget::OnSessionsFound(const TArray<FBlueprintSessionResult>& Results)
{
    FoundSessions = Results;

    if (StatusText)
    {
        if (Results.Num() == 0)
        {
            StatusText->SetText(FText::FromString(TEXT("No LAN sessions found. Try hosting one!")));
        }
        else
        {
            StatusText->SetText(FText::FromString(FString::Printf(TEXT("Found %d session(s)"), Results.Num())));
        }
    }

    // Build display list
    // Note: In a real implementation, you'd populate a ListView with a data source
    // For pure C++, we just log the sessions
    for (int32 i = 0; i < Results.Num(); ++i)
    {
        const FOnlineSessionSearchResult& Result = Results[i].OnlineResult;
        FString SessionName = TEXT("Unknown");
        Result.Session.SessionSettings.Get(FName(TEXT("SESSIONNAME")), SessionName);
        UE_LOG(LogTemp, Log, TEXT("[raceGPS] LAN Session %d: %s (Ping: %dms, Players: %d/%d)"),
            i, *SessionName, Result.PingInMs,
            Result.Session.NumOpenPublicConnections,
            Result.Session.SessionSettings.NumPublicConnections);
    }
}

void ULANBrowserWidget::OnJoinComplete(bool bSuccess)
{
    if (StatusText)
    {
        StatusText->SetText(FText::FromString(bSuccess ? TEXT("Joined! Traveling...") : TEXT("Failed to join session.")));
    }
}

void ULANBrowserWidget::OnHostComplete(bool bSuccess)
{
    if (StatusText)
    {
        StatusText->SetText(FText::FromString(bSuccess ? TEXT("Hosting! Starting server...") : TEXT("Failed to host session.")));
    }
}

void ULANBrowserWidget::UpdateMaxPlayersDisplay()
{
    if (MaxPlayersText && MaxPlayersSlider)
    {
        int32 Val = FMath::RoundToInt(MaxPlayersSlider->GetValue());
        MaxPlayersText->SetText(FText::FromString(FString::Printf(TEXT("Max Players: %d"), Val)));
    }
}
