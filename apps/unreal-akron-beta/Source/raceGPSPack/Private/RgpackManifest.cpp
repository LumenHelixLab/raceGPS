#include "RgpackManifest.h"

#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"

namespace RgpackManifestPrivate
{
    static bool Fail(FString& OutError, const TCHAR* Message)
    {
        OutError = Message;
        return false;
    }

    static bool FailF(FString& OutError, const FString& Message)
    {
        OutError = Message;
        return false;
    }
}

bool URgpackBlueprintLibrary::TryLoadManifest(const FString& PackDir, FRgpackManifest& OutManifest, FString& OutError)
{
    OutError.Reset();

    if (PackDir.IsEmpty())
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("PackDir is empty"));
    }

    const FString ManifestPath = FPaths::Combine(PackDir, TEXT("manifest.json"));
    FString JsonString;
    if (!FFileHelper::LoadFileToString(JsonString, *ManifestPath))
    {
        return RgpackManifestPrivate::FailF(OutError, FString::Printf(TEXT("failed to read manifest: %s"), *ManifestPath));
    }

    TSharedPtr<FJsonObject> Root;
    const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonString);
    if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("manifest.json is not valid JSON object"));
    }

    // schemaVersion == 1
    if (!Root->HasTypedField<EJson::Number>(TEXT("schemaVersion")))
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: schemaVersion"));
    }
    const int32 SchemaVersion = static_cast<int32>(Root->GetNumberField(TEXT("schemaVersion")));
    if (SchemaVersion != 1)
    {
        return RgpackManifestPrivate::FailF(OutError, FString::Printf(TEXT("unsupported schemaVersion: %d"), SchemaVersion));
    }

    // packId / displayName
    FString PackId;
    if (!Root->TryGetStringField(TEXT("packId"), PackId) || PackId.IsEmpty())
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: packId"));
    }
    FString DisplayName;
    if (!Root->TryGetStringField(TEXT("displayName"), DisplayName))
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: displayName"));
    }

    // frame (Frame A)
    const TSharedPtr<FJsonObject>* FramePtr = nullptr;
    if (!Root->TryGetObjectField(TEXT("frame"), FramePtr) || !FramePtr || !FramePtr->IsValid())
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: frame"));
    }
    const TSharedPtr<FJsonObject>& Frame = *FramePtr;

    if (!Frame->HasTypedField<EJson::Number>(TEXT("unitsPerMeter")))
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: frame.unitsPerMeter"));
    }
    const int32 UnitsPerMeter = static_cast<int32>(Frame->GetNumberField(TEXT("unitsPerMeter")));
    if (UnitsPerMeter != 100)
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("frame.unitsPerMeter must be 100 (Frame A)"));
    }

    auto RequireTrue = [&](const TCHAR* Key) -> bool
    {
        if (!Frame->HasTypedField<EJson::Boolean>(Key))
        {
            OutError = FString::Printf(TEXT("missing required field: frame.%s"), Key);
            return false;
        }
        if (Frame->GetBoolField(Key) != true)
        {
            OutError = FString::Printf(TEXT("frame.%s must be true (Frame A)"), Key);
            return false;
        }
        return true;
    };
    if (!RequireTrue(TEXT("zUp")) || !RequireTrue(TEXT("xEast")) || !RequireTrue(TEXT("yNorth")))
    {
        return false;
    }

    if (!Frame->HasTypedField<EJson::Number>(TEXT("originLat"))
        || !Frame->HasTypedField<EJson::Number>(TEXT("originLon"))
        || !Frame->HasTypedField<EJson::Number>(TEXT("originAltM")))
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("frame originLat/originLon/originAltM required"));
    }
    const double OriginLat = Frame->GetNumberField(TEXT("originLat"));
    const double OriginLon = Frame->GetNumberField(TEXT("originLon"));
    const double OriginAltM = Frame->GetNumberField(TEXT("originAltM"));

    // contentHash prefix only (Python owns hash computation)
    FString ContentHash;
    if (!Root->TryGetStringField(TEXT("contentHash"), ContentHash) || !ContentHash.StartsWith(TEXT("sha256:")))
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("contentHash must start with sha256:"));
    }

    // defaults.environmentPreset
    const TSharedPtr<FJsonObject>* DefaultsPtr = nullptr;
    if (!Root->TryGetObjectField(TEXT("defaults"), DefaultsPtr) || !DefaultsPtr || !DefaultsPtr->IsValid())
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: defaults"));
    }
    FString EnvironmentPreset;
    if (!(*DefaultsPtr)->TryGetStringField(TEXT("environmentPreset"), EnvironmentPreset))
    {
        return RgpackManifestPrivate::Fail(OutError, TEXT("missing required field: defaults.environmentPreset"));
    }
    if (EnvironmentPreset != TEXT("Sunset")
        && EnvironmentPreset != TEXT("Twilight")
        && EnvironmentPreset != TEXT("Midnight"))
    {
        return RgpackManifestPrivate::FailF(
            OutError,
            FString::Printf(TEXT("defaults.environmentPreset invalid: %s"), *EnvironmentPreset));
    }

    OutManifest.SchemaVersion = 1;
    OutManifest.PackId = PackId;
    OutManifest.DisplayName = DisplayName;
    OutManifest.ContentHash = ContentHash;
    OutManifest.EnvironmentPreset = EnvironmentPreset;
    OutManifest.OriginLat = OriginLat;
    OutManifest.OriginLon = OriginLon;
    OutManifest.OriginAltM = OriginAltM;
    OutManifest.UnitsPerMeter = 100;
    OutError.Reset();
    return true;
}
