#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "TutorialWidget.generated.h"

UCLASS()
class RACEGPSAKRONBETA_API UTutorialWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    virtual void NativeConstruct() override;

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Tutorial")
    void ShowStep(const FString& Title, const FString& Description, const FString& InputKey);

    UFUNCTION(BlueprintCallable, Category = "raceGPS|Tutorial")
    void HideTutorial();

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* TitleText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* DescriptionText;

    UPROPERTY(meta = (BindWidget))
    class UTextBlock* InputText;

    UPROPERTY(meta = (BindWidget))
    class UButton* SkipButton;

protected:
    UFUNCTION()
    void OnSkipClicked();
};
