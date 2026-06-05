#include "TutorialWidget.h"
#include "Components/TextBlock.h"
#include "Components/Button.h"
#include "TutorialSystem.h"

void UTutorialWidget::NativeConstruct()
{
    Super::NativeConstruct();

    if (SkipButton)
    {
        SkipButton->OnClicked.AddDynamic(this, &UTutorialWidget::OnSkipClicked);
    }
}

void UTutorialWidget::ShowStep(const FString& Title, const FString& Description, const FString& InputKey)
{
    SetVisibility(ESlateVisibility::Visible);

    if (TitleText)
    {
        TitleText->SetText(FText::FromString(Title));
    }
    if (DescriptionText)
    {
        DescriptionText->SetText(FText::FromString(Description));
    }
    if (InputText)
    {
        InputText->SetText(FText::FromString(FString::Printf(TEXT("Press %s to continue"), *InputKey)));
    }
}

void UTutorialWidget::HideTutorial()
{
    SetVisibility(ESlateVisibility::Collapsed);
}

void UTutorialWidget::OnSkipClicked()
{
    UTutorialSystem* Tutorial = NewObject<UTutorialSystem>(this);
    if (Tutorial)
    {
        Tutorial->SkipTutorial();
    }
    HideTutorial();
}
