# raceGPS garage sign template

The final plate of each city intro is a lit sign on a 24-hour garage named raceGPS, shown on the side of a building at night.

## Sign rules (all cities)
- The main word is exactly **raceGPS** (lowercase "race", uppercase "GPS"). It's lettering only, with no icons.
- **Layout:** raceGPS on top. The **city name in flickering neon script** goes below it (for example "Cleveland"). An optional small line such as "24 HOUR GARAGE" / "OPEN 24 HRS" can go under that, and raceGPS stays dominant.
- **Real glass neon, not an LED strip:**
  - round glass tubes with visible bends
  - painted-out blockout sections between letters
  - electrode caps at the tube ends
  - standoff supports
  - a transformer box and cables
  - a hot white-ish core with a coloured halo, and uneven brightness
- **Flicker:** a steady hum with occasional real-neon stutter. One letter or segment drops out briefly, there's a buzz-flicker on power-up, and the glow pulses slightly. Never a uniform LED blink.
- **Colours:** neon green and purple, in two palettes:
  - hard neon: green #39FF14, purple #B026FF, teal-green #00FFA3, violet #7A2CFF
  - neon pastel: mint #9DFFC9, lavender #C9A2FF
- The glow bleeds onto the wall, with reflections on wet pavement below.

## Intro routing
- The intro is chosen by the user's **ZIP code** (not area code).
- A ZIP in a covered city's area gets that city's intro, for example a Cleveland-area ZIP gets the Cleveland intro.
- A ZIP outside every covered area gets the intro of the **nearest biggest covered city**.
- **Each city has its own garage design**, with a different building, wall material, door and sign mounting. What stays constant is raceGPS on top and the city name in flickering neon script below.

## A+C combo direction
- **Styles combined:**
  - wordmark A: Exo 2 Black Italic with a diagonal speed cut
  - wordmark C: Anybody, extra-wide heavy italic, with motion-trail ghosts and neon speed streaks
  - D's underline is dropped
- **Pairing 1:** "race" in Exo 2, "GPS" in Anybody (`garage-AC-1-*`).
- **Pairing 2:** "race" in Anybody, "GPS" in Exo 2 (`garage-AC-2-*`). The Anybody "r" next to the cut can read a bit like "n".
- **GPS crosshair:** a location-fix crosshair (ring, centre dot, four ticks) sits behind "GPS" as a violet glass tube. It's drawn from simple shapes; no icon file is copied.
- **City line:** "Cleveland" in neon script (Sacramento) below, with the most flicker.
- **Construction:** open-face channel letters (dark cans) with an inset glass-neon tube. The ghost trails are horizontal tube slices that fade to the left.
- **Fonts (all SIL Open Font License, Google Fonts):** Exo 2, Anybody, Sacramento, Quicksand, Nunito, Oxanium (labels).

## Chosen direction (2026-10-18)
Garage sign direction = combo 1 (garage-AC-1-race-Exo2_GPS-Anybody-HARD): "race" Exo 2 green with speed cut + motion trails, "GPS" Anybody purple, neon GPS crosshair framed around the P in GPS (as in that first version, not centered behind the whole word), "Cleveland" flickering neon script below.

## Files in this folder
- `garage-signs/garage-1..4-*.jpg/.mp4`: early direction studies (punchy "HARD" neon and softer "PASTEL" neon). They predate the city line, so they show "24 HOUR GARAGE" / "OPEN 24 HRS" instead of "Cleveland".
- `garage-signs/garage-AC-*`: the current A+C combo direction with the GPS crosshair and "Cleveland" script. `.mp4` files are short flicker loops.
- `wordmarks/`: the four earlier wordmark explorations (A speed slash, B glitch split, C motion trail, D neon light-line).
