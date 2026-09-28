#include "RaceAppSubsystem.h"

void URaceAppSubsystem::Initialize(FSubsystemCollectionBase& Collection)
{
    Super::Initialize(Collection);
    UE_LOG(LogTemp, Display, TEXT("app=race"));
}
