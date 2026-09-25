#pragma once

#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "RgpackManifest.generated.h"

/**
 * Read-side RGPACK_v1 manifest fields used by Race.
 * JSON is camelCase (schemaVersion, packId, ...). C++ properties are PascalCase.
 * Does not recompute contentHash — Python owns hashing; C++ validates prefix/presence.
 */
USTRUCT(BlueprintType)
struct RACEGPSPACK_API FRgpackManifest
{
    GENERATED_BODY()

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    int32 SchemaVersion = 0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    FString PackId;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    FString DisplayName;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    FString ContentHash;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    FString EnvironmentPreset;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    double OriginLat = 0.0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    double OriginLon = 0.0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    double OriginAltM = 0.0;

    UPROPERTY(BlueprintReadOnly, Category = "raceGPS|Rgpack")
    int32 UnitsPerMeter = 0;
};

UCLASS()
class RACEGPSPACK_API URgpackBlueprintLibrary : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()

public:
    /**
     * Load and validate <PackDir>/manifest.json against RGPACK_v1 Frame A rules.
     * On failure returns false and fills OutError; OutManifest is left unchanged on early fail
     * but may be partially filled only after successful parse+validate (written on success).
     */
    UFUNCTION(BlueprintCallable, Category = "raceGPS|Rgpack")
    static bool TryLoadManifest(const FString& PackDir, FRgpackManifest& OutManifest, FString& OutError);
};
