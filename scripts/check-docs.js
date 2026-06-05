import { readFileSync, existsSync } from 'node:fs';
import { resolve } from 'node:path';

const ROOT = resolve(import.meta.dirname, '..');
let warnings = 0;

function warn(msg) {
  console.warn(`  \u26a0\ufe0f  ${msg}`);
  warnings++;
}

function readFirstLine(path) {
  try {
    return readFileSync(path, 'utf-8').split('\n')[0].trim();
  } catch {
    return null;
  }
}

function extractTableValue(table, name) {
  const row = table.find(r => r.startsWith('|') && r.includes(name));
  if (!row) return null;
  const cols = row.split('|').map(c => c.trim());
  return cols[2] || null;
}

console.log('\u2500\u2500 Documental integrity check \u2500\u2500');

// 1. INDEX.md vs CHANGELOG.md
const indexPath = resolve(ROOT, 'INDEX.md');
let index;
try {
  index = readFileSync(indexPath, 'utf-8');
} catch {
  warn('INDEX.md not found');
  process.exit(0);
}
const table = index.split('\n').filter(l => l.includes('|') && !l.includes('---') && !l.includes('Archivo'));
const indexVer = extractTableValue(table, 'CHANGELOG.md');
const indexDilig = extractTableValue(table, 'DILIGENCIA.md');

const changelogPath = resolve(ROOT, 'CHANGELOG.md');
let latestTag = null;
try {
  const changelog = readFileSync(changelogPath, 'utf-8');
  const match = changelog.match(/##\s*\[(\d+\.\d+\.\d+)\]/);
  if (match) latestTag = match[1];
} catch {}
if (indexVer && latestTag && indexVer !== latestTag && indexVer !== `v${latestTag}`) {
  warn(`INDEX.md reports CHANGELOG.md v${indexVer}, but latest CHANGELOG tag is v${latestTag}`);
}
if (!latestTag) warn('Could not determine latest version from CHANGELOG.md');

// 2. INDEX.md vs DILIGENCIA.md
const diligPath = resolve(ROOT, 'DILIGENCIA.md');
const firstLine = readFirstLine(diligPath);
let diligVer = null;
if (firstLine) {
  const m = firstLine.match(/v(\d+\.\d+\.\d+)/);
  if (m) diligVer = `v${m[1]}`;
}
if (indexDilig && indexDilig !== '\u2014' && diligVer && indexDilig !== diligVer) {
  warn(`INDEX.md reports DILIGENCIA.md ${indexDilig}, but DILIGENCIA.md header says ${diligVer}`);
}
if (indexDilig === '\u2014' && diligVer) {
  warn(`INDEX.md has DILIGENCIA.md as "\u2014", but file exists with version ${diligVer}`);
}

// 3. No methodology versions in project doc headers
for (const f of ['doc/guias/identidad.md', 'doc/mecanicas/MANDATO.md']) {
  const p = resolve(ROOT, f);
  if (!existsSync(p)) continue;
  const line = readFirstLine(p);
  if (!line) continue;
  const m = line.match(/v(\d+\.\d+\.\d+)/);
  if (m) {
    const ver = m[1];
    if (latestTag && ver !== latestTag && `v${ver}` !== `v${latestTag}`) {
      warn(`${f} has version v${ver} that differs from project version v${latestTag} \u2014 methodology version leaks into project`);
    }
  }
}

// 4. $VARIABLES resolvable from AGENTS.md
const agentsPath = resolve(ROOT, 'AGENTS.md');
try {
  const agents = readFileSync(agentsPath, 'utf-8');
  for (const line of agents.split('\n')) {
    const m = line.match(/^\|\s*\$(\w+)\s*\|\s*(.+?)\s*\|/);
    if (m) {
      const path = m[2].trim().replace(/^`|`$/g, '');
      const full = resolve(ROOT, path);
      if (!existsSync(full)) {
        warn(`$${m[1]} \u2192 ${path} does not exist`);
      }
    }
  }
} catch {}

if (warnings === 0) {
  console.log('  \u2705  No warnings');
}
console.log('');
process.exit(0);
