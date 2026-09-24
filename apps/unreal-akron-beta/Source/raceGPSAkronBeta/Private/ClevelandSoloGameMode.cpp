#include "ClevelandSoloGameMode.h"
#include "ClevelandLookDirector.h"
#include "ChaosVehiclePawn.h"
#include "AkronXodrImporter.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "Engine/World.h"
#include "TimerManager.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Engine.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonSerializer.h"
#include "Dom/JsonObject.h"

AClevelandSoloGameMode::AClevelandSoloGameMode()
{
	PrimaryActorTick.bCanEverTick = true;
	DefaultPawnClass = AChaosVehiclePawn::StaticClass();
	VisualPreset = EClevelandVisualMode::Sunset;
}

void AClevelandSoloGameMode::BeginPlay()
{
	Super::BeginPlay();
	ResolvePresetFromCommandLine();
	SpawnLookDirector();
	TryTeleportPlayerToBurkeStart();
	LogSoloReady();

	FString CaptureLabel;
	if (FParse::Value(FCommandLine::Get(), TEXT("ClevelandCapture="), CaptureLabel) && !CaptureLabel.IsEmpty())
	{
		PendingCaptureLabel = CaptureLabel;
		bCapturePending = true;
		CaptureElapsed = 0.f;
		UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] capture armed label=%s delay=%.1fs"), *PendingCaptureLabel, CaptureDelay);
	}
}

void AClevelandSoloGameMode::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	ReadyElapsed += DeltaSeconds;

	if (!bTeleported && ReadyElapsed < 5.f)
	{
		if (TryTeleportPlayerToBurkeStart())
		{
			// ok
		}
	}

	if (!bLoggedReady && ReadyElapsed > 1.0f)
	{
		LogSoloReady();
		bLoggedReady = true;
	}

	if (bCapturePending)
	{
		CaptureElapsed += DeltaSeconds;
		if (CaptureElapsed >= CaptureDelay)
		{
			bCapturePending = false;
			CaptureHighResStill(PendingCaptureLabel.IsEmpty() ? TEXT("solo") : PendingCaptureLabel);
		}
	}
}

void AClevelandSoloGameMode::ResolvePresetFromCommandLine()
{
	FString PresetName;
	if (FParse::Value(FCommandLine::Get(), TEXT("ClevelandPreset="), PresetName) && !PresetName.IsEmpty())
	{
		EClevelandVisualMode Parsed;
		if (AClevelandLookDirector::TryParsePresetName(PresetName, Parsed))
		{
			VisualPreset = Parsed;
			UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] cmdline preset=%s"), *AClevelandLookDirector::PresetDisplayName(Parsed));
		}
		else
		{
			UE_LOG(LogTemp, Warning, TEXT("[raceGPS Cleveland] unknown ClevelandPreset=%s (use Sunset|Twilight|Midnight)"), *PresetName);
		}
	}
}

void AClevelandSoloGameMode::SpawnLookDirector()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	FActorSpawnParameters Params;
	Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	LookDirector = World->SpawnActorDeferred<AClevelandLookDirector>(
		AClevelandLookDirector::StaticClass(), FTransform::Identity, nullptr, nullptr,
		ESpawnActorCollisionHandlingMethod::AlwaysSpawn);
	if (LookDirector)
	{
		LookDirector->Mode = VisualPreset;
		LookDirector->FinishSpawning(FTransform::Identity);
		LookDirector->ApplyVisualMode(VisualPreset);
	}
}

void AClevelandSoloGameMode::ClevelandPreset(const FString& Name)
{
	EClevelandVisualMode Parsed;
	if (!AClevelandLookDirector::TryParsePresetName(Name, Parsed))
	{
		UE_LOG(LogTemp, Warning, TEXT("[raceGPS Cleveland] ClevelandPreset: expected Sunset|Twilight|Midnight got '%s'"), *Name);
		return;
	}
	VisualPreset = Parsed;
	if (!LookDirector && GetWorld())
	{
		LookDirector = GetWorld()->SpawnActor<AClevelandLookDirector>(AClevelandLookDirector::StaticClass());
	}
	if (LookDirector)
	{
		LookDirector->ApplyVisualMode(Parsed);
	}
}

void AClevelandSoloGameMode::ClevelandCaptureStill(const FString& Label)
{
	CaptureHighResStill(Label.IsEmpty() ? TEXT("manual") : Label);
}

FString AClevelandSoloGameMode::ResolveCityPackFile(const FString& FileName) const
{
	const FString ProjectDir = FPaths::ProjectDir();
	TArray<FString> Candidates;
	Candidates.Add(ProjectDir / CityPackRelativeDir / FileName);
	Candidates.Add(ProjectDir / TEXT("../../") / CityPackRelativeDir / FileName);
	Candidates.Add(FPaths::ConvertRelativePathToFull(ProjectDir / TEXT("../../citypacks/cleveland/burke_gp_1997") / FileName));
	for (const FString& C : Candidates)
	{
		const FString Full = FPaths::ConvertRelativePathToFull(C);
		if (FPaths::FileExists(Full))
		{
			return Full;
		}
	}
	return FString();
}

bool AClevelandSoloGameMode::TryTeleportPlayerToBurkeStart()
{
	UWorld* World = GetWorld();
	if (!World || bTeleported)
	{
		return bTeleported;
	}

	APlayerController* PC = World->GetFirstPlayerController();
	if (!PC || !PC->GetPawn())
	{
		return false;
	}

	const FString LinePath = ResolveCityPackFile(TEXT("racing_line.json"));
	if (LinePath.IsEmpty())
	{
		UE_LOG(LogTemp, Warning, TEXT("[raceGPS Cleveland] racing_line.json not found under %s — spawn stays at PlayerStart"), *CityPackRelativeDir);
		bTeleported = true; // don't spam
		return false;
	}

	FString JsonStr;
	if (!FFileHelper::LoadFileToString(JsonStr, *LinePath))
	{
		UE_LOG(LogTemp, Warning, TEXT("[raceGPS Cleveland] failed to read %s"), *LinePath);
		bTeleported = true;
		return false;
	}

	TSharedPtr<FJsonObject> Root;
	const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(JsonStr);
	if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
	{
		UE_LOG(LogTemp, Warning, TEXT("[raceGPS Cleveland] racing_line.json parse failed"));
		bTeleported = true;
		return false;
	}

	double OriginLat = 41.51722;
	double OriginLon = -81.68306;
	const TSharedPtr<FJsonObject>* OriginObj = nullptr;
	if (Root->TryGetObjectField(TEXT("origin"), OriginObj) && OriginObj && (*OriginObj).IsValid())
	{
		(*OriginObj)->TryGetNumberField(TEXT("lat"), OriginLat);
		(*OriginObj)->TryGetNumberField(TEXT("lon"), OriginLon);
	}

	const TArray<TSharedPtr<FJsonValue>>* Samples = nullptr;
	if (!Root->TryGetArrayField(TEXT("samples"), Samples) || !Samples || Samples->Num() == 0)
	{
		UE_LOG(LogTemp, Warning, TEXT("[raceGPS Cleveland] racing_line.json has no samples"));
		bTeleported = true;
		return false;
	}

	const TSharedPtr<FJsonObject> S0 = (*Samples)[0]->AsObject();
	double Lat = OriginLat;
	double Lon = OriginLon;
	double HeadingDeg = 247.684;
	S0->TryGetNumberField(TEXT("lat"), Lat);
	S0->TryGetNumberField(TEXT("lon"), Lon);
	S0->TryGetNumberField(TEXT("heading_deg"), HeadingDeg);

	// Frame A: X=east Y=north Z-up 1uu=1cm. UE yaw 0 = +X = east; compass 0=N, 90=E => UE yaw = compass-90.
	const FVector WorldLoc = UAkronXodrImporter::GeoToWorld(Lat, Lon, OriginLat, OriginLon) + FVector(0.f, 0.f, SpawnHeightCm);
	const FRotator WorldRot(0.f, static_cast<float>(HeadingDeg) - 90.f, 0.f);

	PC->GetPawn()->SetActorLocationAndRotation(WorldLoc, WorldRot, false, nullptr, ETeleportType::ResetPhysics);
	bTeleported = true;

	UE_LOG(LogTemp, Log,
		TEXT("[raceGPS Cleveland] solo teleport S/F lat=%.6f lon=%.6f heading=%.1f -> loc=(%.1f,%.1f,%.1f) yaw=%.1f pack=%s"),
		Lat, Lon, HeadingDeg, WorldLoc.X, WorldLoc.Y, WorldLoc.Z, WorldRot.Yaw, *LinePath);
	return true;
}

void AClevelandSoloGameMode::CaptureHighResStill(const FString& Phase)
{
	const FString EvidenceDir = FPaths::ConvertRelativePathToFull(
		FPaths::ProjectDir() / TEXT("../../docs/evidence/grokbot/G4-packaged-solo-visual/stills"));
	IFileManager::Get().MakeDirectory(*EvidenceDir, true);
	const FString Preset = AClevelandLookDirector::PresetDisplayName(VisualPreset);
	const FString Stem = FString::Printf(TEXT("cleveland_%s_%s"), *Preset.ToLower(), *Phase);
	const FString FullPathNoExt = EvidenceDir / Stem;

	// Standard viewport shot (writes under Saved/Screenshots) + absolute-path request.
	if (GEngine)
	{
		GEngine->Exec(GetWorld(), TEXT("Shot"));
		GEngine->Exec(GetWorld(), TEXT("HighResShot 1"));
	}
	FScreenshotRequest::RequestScreenshot(FullPathNoExt, false, false);
	UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] Shot/HighResShot/FScreenshotRequest armed stem=%s"), *FullPathNoExt);

	if (FParse::Param(FCommandLine::Get(), TEXT("ClevelandAutoQuit")))
	{
		if (UWorld* World = GetWorld())
		{
			FTimerHandle QuitHandle;
			World->GetTimerManager().SetTimer(QuitHandle, FTimerDelegate::CreateLambda([World]()
			{
				UE_LOG(LogTemp, Log, TEXT("[raceGPS Cleveland] ClevelandAutoQuit after screenshot flush"));
				if (GEngine)
				{
					GEngine->Exec(World, TEXT("quit"));
				}
			}), 6.0f, false);
		}
	}
}

void AClevelandSoloGameMode::LogSoloReady()
{
	APlayerController* PC = GetWorld() ? GetWorld()->GetFirstPlayerController() : nullptr;
	APawn* Pawn = PC ? PC->GetPawn() : nullptr;
	UE_LOG(LogTemp, Log,
		TEXT("[raceGPS Cleveland] SOLO READY product=%s circuit=%s preset=%s pawn=%s teleported=%d pack=%s PROVISIONAL (not certified 2006)"),
		*ProductTitle,
		*CircuitTitle,
		*AClevelandLookDirector::PresetDisplayName(VisualPreset),
		Pawn ? *Pawn->GetClass()->GetName() : TEXT("none"),
		bTeleported ? 1 : 0,
		*CityPackRelativeDir);
}
