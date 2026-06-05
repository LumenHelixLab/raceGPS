import { readFileSync, writeFileSync } from 'node:fs';

const raw = JSON.parse(readFileSync('D:/projects/racegps/akron_buildings_raw.json', 'utf-8'));
const citypack = JSON.parse(readFileSync('D:/projects/racegps/akron_citypack.json', 'utf-8'));

// Build node map
const nodes = new Map<number, { lat: number; lon: number }>();
for (const el of raw.elements) {
  if (el.type === 'node') {
    nodes.set(el.id, { lat: el.lat, lon: el.lon });
  }
}

function parseHeight(value: string | undefined): number | undefined {
  if (!value) return undefined;
  const num = parseFloat(value.replace(/\s*m$/, ''));
  return isNaN(num) ? undefined : num;
}

function parseLevels(value: string | undefined): number | undefined {
  if (!value) return undefined;
  const num = parseFloat(value);
  return isNaN(num) ? undefined : num;
}

function roofTypeFromTag(tag: string | undefined): 'flat' | 'gabled' | 'hipped' | 'pyramidal' | undefined {
  if (!tag) return undefined;
  switch (tag) {
    case 'flat': return 'flat';
    case 'gabled': case 'gabel': return 'gabled';
    case 'hipped': case 'hip': return 'hipped';
    case 'pyramidal': case 'pyramid': return 'pyramidal';
    default: return undefined;
  }
}

const buildings: any[] = [];

for (const el of raw.elements) {
  if (el.type !== 'way' || !el.tags?.building) continue;

  const ring = el.nodes.map((id: number) => nodes.get(id)).filter(Boolean);
  if (ring.length < 3) continue;

  const tags = el.tags;
  const height = parseHeight(tags.height) || parseHeight(tags.est_height) || parseHeight(tags['building:height']);
  const levels = parseLevels(tags['building:levels']) || parseLevels(tags.levels);
  const minHeight = parseHeight(tags.min_height);
  const minLevel = parseLevels(tags['building:min_level']);
  const roofType = roofTypeFromTag(tags['roof:shape']);
  const roofOrientation = tags['roof:orientation'] === 'across' ? 'across' : tags['roof:orientation'] === 'along' ? 'along' : undefined;

  // Estimate height from levels if not given
  let computedHeight = height;
  let computedLevels = levels;
  if (computedHeight === undefined) {
    if (computedLevels !== undefined) {
      computedHeight = computedLevels * 3.5 + (roofType === 'flat' ? 0 : 2);
    } else {
      computedLevels = 1;
      computedHeight = 4;
    }
  } else if (computedLevels === undefined) {
    computedLevels = Math.max(1, Math.round((computedHeight - (roofType === 'flat' ? 0 : 2)) / 3.5));
  }

  // Compute minHeight
  let computedMinHeight = minHeight;
  if (computedMinHeight === undefined && minLevel !== undefined) {
    computedMinHeight = minLevel * 3.5;
  }

  buildings.push({
    id: String(el.id),
    rings: [ring],
    height: computedHeight,
    minHeight: computedMinHeight || 0,
    levels: computedLevels,
    roofType: roofType || 'flat',
    roofOrientation,
    hasWindows: computedLevels > 1 && computedHeight - (computedMinHeight || 0) > 3,
  });
}

console.log(`Processed ${buildings.length} buildings`);

// Add buildings to citypack
citypack.buildings = buildings;

writeFileSync('D:/projects/racegps/akron_citypack.json', JSON.stringify(citypack, null, 2));
console.log('Saved to akron_citypack.json');
