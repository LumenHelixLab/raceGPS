const path = require('path');

const MAX_SIZE_MB = 50;
const MAX_SIZE_BYTES = MAX_SIZE_MB * 1024 * 1024;

const ALLOWED_EXTENSIONS = new Set([
  '.json', '.png', '.jpg', '.jpeg', '.fbx', '.umap', '.uasset', '.ini'
]);

const FORBIDDEN_EXTENSIONS = new Set([
  '.exe', '.bat', '.sh', '.cmd', '.com', '.scr', '.msi', '.dll'
]);

const PROFANITY_LIST = [
  'shit', 'fuck', 'damn', 'bitch', 'asshole', 'cunt', 'dick', 'piss', 'hell'
];

function hasProfanity(text) {
  if (!text) return false;
  const lower = text.toLowerCase();
  return PROFANITY_LIST.some(word => lower.includes(word));
}

function validateManifest(manifest) {
  const required = ['name', 'version', 'author', 'routes'];
  const missing = required.filter(k => manifest[k] === undefined);
  if (missing.length) {
    return { valid: false, error: `Missing manifest fields: ${missing.join(', ')}` };
  }
  if (typeof manifest.name !== 'string' || manifest.name.length < 2) {
    return { valid: false, error: 'City name must be at least 2 characters' };
  }
  if (hasProfanity(manifest.name)) {
    return { valid: false, error: 'City name contains inappropriate language' };
  }
  if (!Array.isArray(manifest.routes) || manifest.routes.length === 0) {
    return { valid: false, error: 'Manifest routes must be a non-empty array' };
  }
  return { valid: true };
}

function validateZipEntries(entries) {
  let hasManifest = false;
  for (const entry of entries) {
    const ext = path.extname(entry.name).toLowerCase();
    if (FORBIDDEN_EXTENSIONS.has(ext)) {
      return { valid: false, error: `Forbidden file type: ${ext}` };
    }
    if (!ALLOWED_EXTENSIONS.has(ext) && ext !== '') {
      return { valid: false, error: `Disallowed file type: ${ext}` };
    }
    if (entry.name.toLowerCase() === 'manifest.json' || entry.name.toLowerCase().endsWith('/manifest.json')) {
      hasManifest = true;
    }
  }
  if (!hasManifest) {
    return { valid: false, error: 'Missing manifest.json in archive' };
  }
  return { valid: true };
}

function validateFileSize(size) {
  if (size > MAX_SIZE_BYTES) {
    return { valid: false, error: `File exceeds ${MAX_SIZE_MB}MB limit` };
  }
  return { valid: true };
}

module.exports = {
  MAX_SIZE_BYTES,
  ALLOWED_EXTENSIONS,
  FORBIDDEN_EXTENSIONS,
  hasProfanity,
  validateManifest,
  validateZipEntries,
  validateFileSize
};
