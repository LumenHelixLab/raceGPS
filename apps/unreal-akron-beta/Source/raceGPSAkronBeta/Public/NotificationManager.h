// Copyright raceGPS. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "NotificationManager.generated.h"

/**
 * Single notification entry in the queue.
 */
USTRUCT(BlueprintType)
struct FNotificationData
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Notification")
    FString Title;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Notification")
    FString Body;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Notification")
    FString IconPath;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Notification")
    float DisplayDuration = 3.0f;
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnNotificationShown, FNotificationData, Notification);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnNotificationQueueEmpty);

/**
 * Queue-based notification manager for in-game pop-ups.
 * Blueprints bind to OnNotificationShown to drive UMG widgets.
 */
UCLASS()
class RACEGPSAKRONBETA_API UNotificationManager : public UObject
{
    GENERATED_BODY()

public:
    UNotificationManager();

    /** Enqueue a new notification. If the queue was empty it displays immediately. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Notification")
    void ShowNotification(const FString& Title, const FString& Body, const FString& Icon);

    /** Remove all pending notifications. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Notification")
    void ClearQueue();

    /** True if no notifications are queued or displaying. */
    UFUNCTION(BlueprintPure, Category = "raceGPS|Notification")
    bool IsQueueEmpty() const { return NotificationQueue.IsEmpty(); }

    /** Get the next notification in the queue without removing it. */
    UFUNCTION(BlueprintPure, Category = "raceGPS|Notification")
    FNotificationData PeekNextNotification() const;

    /** Tick the manager to advance display timers. Should be called by the owning widget or GameMode each frame. */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Notification")
    void TickManager(float DeltaTime);

    /** Delegate fired when a notification is ready to be displayed. */
    UPROPERTY(BlueprintAssignable, Category = "raceGPS|Notification")
    FOnNotificationShown OnNotificationShown;

    /** Delegate fired when the queue becomes empty. */
    UPROPERTY(BlueprintAssignable, Category = "raceGPS|Notification")
    FOnNotificationQueueEmpty OnQueueEmpty;

    /** Default duration for notifications (seconds). */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Notification")
    float DefaultDisplayDuration = 3.0f;

    /** Maximum queue size to prevent unbounded growth. */
    UPROPERTY(EditDefaultsOnly, BlueprintReadOnly, Category = "raceGPS|Notification")
    int32 MaxQueueSize = 32;

protected:
    UPROPERTY()
    TArray<FNotificationData> NotificationQueue;

    UPROPERTY()
    float CurrentDisplayTime = 0.0f;
};
