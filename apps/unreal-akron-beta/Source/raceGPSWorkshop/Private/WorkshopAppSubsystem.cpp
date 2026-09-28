#include "WorkshopAppSubsystem.h"

void UWorkshopAppSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Display, TEXT("app=workshop"));
}
