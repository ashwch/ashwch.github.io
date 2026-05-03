import { readFileSync } from 'node:fs';
import path from 'node:path';

const ABBREVIATIONS_PATH = path.resolve(process.cwd(), '..', 'abbreviations.md');
const ABBREVIATION_PATTERN = /^\*\[([^\]]+)\]:\s*(.+)$/;

function loadAbbreviations() {
  const source = readFileSync(ABBREVIATIONS_PATH, 'utf8');
  return Object.fromEntries(
    source
      .split(/\r?\n/)
      .map((line) => line.match(ABBREVIATION_PATTERN))
      .filter((match): match is RegExpMatchArray => Boolean(match))
      .map(([, key, value]) => [key, value.trim()]),
  );
}

export const abbreviations = loadAbbreviations();
