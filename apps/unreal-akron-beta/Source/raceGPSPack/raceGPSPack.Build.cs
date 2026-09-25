using UnrealBuildTool;

public class raceGPSPack : ModuleRules
{
    public raceGPSPack(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp20;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "Json",
            "JsonUtilities"
        });

        PublicIncludePaths.AddRange(new string[]
        {
            ModuleDirectory + "/Public"
        });

        PrivateIncludePaths.AddRange(new string[]
        {
            ModuleDirectory + "/Private"
        });
    }
}
