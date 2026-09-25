using UnrealBuildTool;

public class raceGPSWorkshop : ModuleRules
{
    public raceGPSWorkshop(ReadOnlyTargetRules Target) : base(Target)
    {
        PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
        CppStandard = CppStandardVersion.Cpp20;

        PublicDependencyModuleNames.AddRange(new string[]
        {
            "Core",
            "CoreUObject",
            "Engine",
            "raceGPSPack"
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
