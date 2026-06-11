# raceGPS UX Polish Punch List

Completed in code
- Main menu now exposes premium-facing summary helpers for blueprint binding:
  - BuildDriveSummaryText()
  - BuildLaunchButtonText()
  - BuildVersionLine()
  - BuildVehicleClassLabel()
- Main menu title now frames the fantasy clearly:
  - "raceGPS — Midnight Club on real roads"
- Vehicle card copy now reads like a product surface, not a debug dump.
- Handling card now includes the launch CTA context.
- Onboarding now exposes step subtitles for each first-run stage.
- Onboarding now writes a clear completion verdict message into PlayerSettings.json.

Bind next in Unreal
- MainMenu blueprint:
  - TitleText
  - VersionText
  - VehicleInfoText
  - HandlingInfoText
  - HandlingSelector
  - RouteSelector
  - VehicleSelector
- Optional UX enhancement:
  - show BuildLaunchButtonText() on or near the Play button label
  - show BuildDriveSummaryText() as the hero subheading under the title
- Onboarding blueprint:
  - show GetStepSubtitle(CurrentStep) under each step title
  - show completion_message at the final confirmation screen

Pass condition
- first screen reads like a racing product
- selected car + handling + route are obvious at a glance
- onboarding ends with a simple yes/no readiness message
