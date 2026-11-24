// news-image-20261124: one image summing up Tuesday 24 November 2026.
//
// The poster itself (entry.png, 1024x1024) was drawn by draw.py in this
// repository with flat shapes and DejaVu text, so every headline is crisp
// and nothing in it is garbled. This program has a single job: copy that
// exact file to the grader's output directory, unchanged, after checking
// it really is the PNG we drew and that it fits the competition's limits.
//
// Node 22, standard library only: nothing is installed before it runs,
// there is no network access, and the copy is byte-for-byte identical on
// every run, so the grader's two runs write the same bytes.
//
// Outside the grader's container, MAKEFUN_OUTPUT_DIR stands in for /output:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync, readFileSync, statSync } from 'node:fs';
import { join } from 'node:path';

const IMAGE = 'entry.png';
const MAX_PIXELS = 1024;
const MAX_BYTES = 1024 * 1024;
const PNG_SIGNATURE = [0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a];

const source = new URL(`./${IMAGE}`, import.meta.url);
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const target = join(outDir, IMAGE);

const bytes = readFileSync(source);

if (!PNG_SIGNATURE.every((byte, i) => bytes[i] === byte)) {
  throw new Error(`${IMAGE} does not start with the PNG signature`);
}
const width = bytes.readUInt32BE(16);
const height = bytes.readUInt32BE(20);
if (width > MAX_PIXELS || height > MAX_PIXELS) {
  throw new Error(`${IMAGE} is ${width}x${height}, over the ${MAX_PIXELS}x${MAX_PIXELS} limit`);
}
if (bytes.length > MAX_BYTES) {
  throw new Error(`${IMAGE} is ${bytes.length} bytes, over the 1 MiB limit`);
}

mkdirSync(outDir, { recursive: true });
copyFileSync(source, target);

// Read back what was written and confirm it is the same whole PNG:
// a partial or altered copy must fail loudly instead of being judged.
const written = readFileSync(target);
if (written.length !== bytes.length || !written.equals(bytes)) {
  throw new Error(`copied file differs from ${IMAGE}`);
}
if (statSync(target).size !== bytes.length) {
  throw new Error(`copied ${statSync(target).size} bytes, expected ${bytes.length}`);
}

console.log(`wrote ${target} (${width}x${height}, ${bytes.length} bytes)`);
