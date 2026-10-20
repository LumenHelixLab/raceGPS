# Dead Man's Curve (Cleveland, I-90 "Innerbelt Curve"): OSM geometry notes
Data: OpenStreetMap via Overpass API (overpass-api.de), pulled 2026-10-18 ~8:24 PM ET
(OSM base timestamp 2026-10-19T00:21Z). (c) OpenStreetMap contributors, ODbL.
Raw Overpass query results are not included here (available on request); the plot is osm-curve.png.
Plot: osm-curve.png (© OpenStreetMap contributors)

## Location
The curve is NOT at E 55th. OSM way 981471310 (I-90 EB, name "Innerbelt", **alt_name "Dead Man's Curve"**)
runs 41.51617,-81.67489 -> 41.51851,-81.67403, apex ~41.5170,-81.6754, by E 26th St / Lakeside Ave,
directly SE of Burke Lakefront Airport's east end. E 55th is ~2 km further east on the Shoreway
(it appears only as a lane destination: "East 55th Street; Marginal Roads").

## Eastbound geometry (computed from way node coordinates, local flat projection)
- Approach: I-90 EB "Innerbelt" runs roughly NORTH out of downtown (heading 346 deg, bending to ~326-330 deg / NNW just before the curve).
- Curve: heading **~325 deg -> ~51 deg** = **~86 deg turn to the RIGHT** (clockwise).
- Curved section length ~265 m (~870 ft); whole tagged way 322 m.
- Radius: circle fit over the way ~150 m; tightest part (335->51 deg over ~156 m) ~125 m. So about 120-175 m (~400-575 ft).
- Exit: straightens to ~55 deg (ENE) as the Cleveland Memorial Shoreway (I-90 + SR 2), running along the lake toward E 55th/E 72nd, Euclid, Erie PA.

## Tags on the curve (way 981471310)
lanes=4, maxspeed=50 mph, **maxspeed:advisory=35 mph**, oneway=yes, surface=asphalt, hgv=designated.
destination:lanes = Euclid;Erie Pa | Euclid;Erie Pa | Euclid;Erie Pa;Lakewood | Lakewood
turn:lanes = none|none|through;right|right (right lane exits 174B to SR 2 West / Lakewood / Port of Cleveland).
lit: NOT tagged in OSM (no lighting data). No bridge/layer tag on the I-90 curve itself.
After the curve: way 1473490119 / 1041352343 "I 90;SR 2", 5 lanes (SR 2 EB merges), then 4 lanes, maxspeed 60 mph from ~41.5258,-81.6601 on.

## Route 2 relationship
- Eastbound: SR 2 EB (Shoreway from downtown, along Burke) crosses OVER the I-90 curve on a bridge
  (way 75641123, bridge=yes layer=1, 3 lanes, ~41.5168,-81.6755) and merges into I-90 from the RIGHT at ~41.5221,-81.6672.
  From there east they are one road: I-90 / SR 2 Cleveland Memorial Shoreway. For eastbound traffic, Route 2 does not split off; it joins.
- Westbound: SR 2 West splits off at ~41.52040,-81.67087 (way 49684111, destination:ref "SR 2 West") and continues SW along the lake past Burke,
  while I-90 WB swings LEFT into the curve.
- Exits around the curve (EB): 174A Lakeside Ave (right, before the curve), 174B SR 2 West/Lakewood (right lane, end of the curve), 196C South Marginal Rd.

## What's on each side (eastbound), from OSM
Before the curve (heading NNW): LEFT = downtown/Burke direction (west); rail bridges cross overhead near 41.514 (NS Cleveland Line, Silver Plate track)
and at ~41.516 (Cleveland Terminal Subdivision, Cleveland Port Railway x2, South Marginal Rd, all bridge layer=1) just before the turn-in.
After the curve (heading ENE ~51-55 deg):
- LEFT: Burke Lakefront Airport (runways 06L/24R and 06R/24L run parallel at heading ~060, east ends at -81.6716 / -81.6757,
  aerodrome boundary to -81.6666), then Lake Erie with breakwaters, a marina and Lakeside Yacht Club, then the Cleveland Public Power plant
  (41.526,-81.662) and twin water towers (~41.523,-81.661).
- RIGHT: Cleveland Police Mounted Unit stable, Arconic industrial plant, Ariel International Center, rail lines (Cleveland Terminal Subdivision)
  running parallel, then St Clair-Superior neighborhood (E 40th, St Clair Ave). The WABQ radio tower is further east (~41.527,-81.653) on the right.
- Downtown skyline: behind-left once you're out of the curve (it's to the west/southwest).

## Geometry checks
1. Heading east out of downtown, it's a **RIGHT-hand** turn: confirmed. Eastbound heading goes 325 -> 51 deg, about 86 deg clockwise.
2. Coming around it eastbound, **Burke Lakefront Airport is on the LEFT**: confirmed. All four runway endpoints are left of the curve's exit tangent. Lake Erie is also on the left.

## Web sources (signage, history, crashes)
- ODOT PIO Amanda McFarland (2022): "That is a 90-degree curve"; mitigation is "rumble strips, bright flashing lights, and overhead signs";
  drivers slow from 55 to 35; frequent truck rollovers. https://www.cleveland19.com/2022/07/21/it-will-happen-changes-eventually-come-dead-mans-curve-i-90-cleveland/
- Cleveland Magazine, CLE Myths: flashing lights and rumble strips, 35 mph from 50, ~90,000 vehicles/day, 526 crashes / 0 deaths / 150 injuries in a decade, >50% rear-end or sideswipe.
  https://clevelandmagazine.com/articles/cle-myths-dead-mans-curve/
- cleveland.com (2023): "the 90-degree turn on Interstate 90 in front of Burke Lakefront Airport"; ODOT calls it the "Innerbelt Curve".
  https://www.cleveland.com/news/2023/12/why-its-called-dead-mans-curve-and-whether-the-name-really-fits.html
- News5 (Jan 2025): 28 crashes since Jan 6; most in the far-left/center lanes sliding into the center barrier; ODOT added a
  "Slow Down. Sharp Curve Ahead" sign. https://www.news5cleveland.com/traffic/traffic-news/slow-down-sharp-curve-ahead-new-sign-put-up-on-dead-mans-curve-following-multiple-crashes
  https://www.news5cleveland.com/news/local-news/odot-engineers-close-lane-at-dead-mans-curve-to-investigate-uptick-in-crashes
- News5: opened 1962, at first with no banking, rumble strips or adequate signs; the curve exists because land tied to Burke was not available;
  ODOT's Innerbelt Modernization study could take 10-15 years. https://www.news5cleveland.com/news/local-news/we-follow-through/slowly-how-to-drive-dead-mans-curve-and-how-long-it-takes-to-fix-it
- Cleveland19 (2024): EB curve ranked #16 statewide for safety need; design funding for Superior Ave to E 49th; 212 crashes in 5 years (OSHP).
  https://www.cleveland19.com/2024/08/26/step-closer-changes-dead-mans-curve/ , https://www.cleveland19.com/2024/08/28/how-deadly-is-dead-mans-curve/
- No source found for a "2000s reconstruction"; the sources describe safety add-ons over the decades and a redesign that is still in study.

## Caveats
- OSM has no lighting tag here. Flashing warning lights and overhead signs come from news and ODOT quotes, not from OSM.
- Plot: the lake label and blue lines are breakwaters; the actual shoreline sits just north of the Burke runways.
- Radius and angles are computed from OSM centerline nodes and are approximate.

## Visual notes from public drive videos (approximate, by eye; see SOURCES.md for links)
- East 55th (Exit 175) is the next exit after the curve heading east, about 1.25 mi on (OSM puts it ~2 km east).
- Just before the bend, the road passes under a rusted steel railroad bridge on concrete piers carrying green/yellow "I-90/2 EAST 35 MPH" and "2 WEST 35 MPH EXIT ONLY" curve-arrow signs.
- In the bend itself, the road runs under a long concrete ramp overpass on rows of round pillars, with concrete ramps rising on both sides and flashing amber arrow boards.
- The intro's all-amber lighting under that span is a creative choice; in 2018 night footage the fixtures look whitish.
- Route 2 merges from the RIGHT just after the bend, and the road widens (consistent with OSM).
