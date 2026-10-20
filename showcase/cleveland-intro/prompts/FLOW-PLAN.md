# Production plan: raceGPS Cleveland cinematic intro

**Status: draft.** Prompts are written; no final video has been produced yet.

## Structure: five 10-second scenes (~50 s)
| Scene | Seq | Content | Callout |
|---|---|---|---|
| 1 | 0:00–0:10 | I-77 N into downtown, skyline ahead, onto the I-90 E Innerbelt (4 lanes, center barrier), under the Euclid and Superior Avenue overpasses | INNERBELT |
| 2 | 0:10–0:20 | Lakeside Ave exit, then the rusted steel rail bridge on concrete piers with green-over-yellow "I-90/2 EAST 35 MPH" curve-arrow signs, a dark underpass, then the ~86° RIGHT bend (~870 ft) under the long pillared concrete ramp overpass, amber light under the whole span plus flashing amber arrow boards. First tiny red/blue lights in a mirror. | DEAD MAN'S CURVE |
| 3 | 0:20–0:30 | Memorial Shoreway heading NE: Burke Lakefront Airport on the LEFT with Lake Erie beyond; Route 2 merges from the RIGHT and the road widens to 5 lanes; police only in mirrors or wide side views; East 55th gantry ahead (~1.25 mi past the curve) | ROUTE 2 EAST |
| 4 | 0:30–0:40 | Under the East 55th gantry the racers dust the police and the sirens fade; low camera looking back west at the skyline under a black sky and a big full moon; the cars blast past and the frame settles into the logo plate | LOSE THE HEAT, then raceGPS |
| 5 | 0:40–0:50 | Outro: cars parked on the lakefront under the full moon, skyline across the water; empty glowing panel, bars and tiles for credits, announcements and links | see POST-EDIT-OVERLAYS.md |

## Creative rules applied to every scene
- **Real place, real route.** Geometry comes from OpenStreetMap and public drive videos (see `../research/`).
- **Realistic night footage**: natural color, true blacks, practical light only, wet-sheen asphalt (no rain or puddles), real camera rigs (camera car, bumper mount, chase car, drone).
- **Game-art layer on top**: Midnight Club-style light streaks, speed lines, glitch lines and graphic wipes in raceGPS red with purple, green and blue cyber neon. They leave clean, empty glowing panels.
- **Police stay in the background**: only seen in a racer's mirror or a wide side view, never close, no contact. Their red and blue light washes over paint, chrome and glass; sirens fade as the racers pull away.
- **No generated lettering**: every word, callout and the logo is added in the edit (DaVinci Resolve). The prompts ask for empty panels.
- **Anti-artifact rules**: every vehicle drives forward, nose-first; headlights front only, taillights rear only; four wheels on the road; no morphing, duplicated or backwards cars.
- Same two hero cars throughout: a candy-blue widebody Japanese-style import coupe and a black American muscle car with a hood scoop. Generic, no real brands or badges.

## How the clips get made
- Text-to-video, 16:9, 10-second clips; scenes can be chained by using the last frame of one clip as the first frame of the next.
- Prompts use timestamped beats (`[00:00-00:02] ...`) to pack several camera moves into one clip, per Google's Veo prompting guide: https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1
- Each prompt is kept under ~750 tokens.

## Open notes
- The amber lighting under the curve's overpass is a creative choice; in 2018 night footage the fixtures look whitish.
- Route 2 merges from the right eastbound (confirmed from OSM and drive footage).
