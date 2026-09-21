const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const read = file => fs.readFileSync(path.join(root, file), 'utf8');

test('PWA manifest identifies the standalone app and its local icon', () => {
  const manifest = JSON.parse(read('public/manifest.webmanifest'));
  assert.equal(manifest.name, 'GaitTrace');
  assert.equal(manifest.display, 'standalone');
  assert.equal(manifest.start_url, './');
  assert.equal(manifest.scope, './');
  assert.equal(manifest.orientation, 'portrait');
  assert.deepEqual(manifest.icons, [{ src: 'icon.svg', sizes: 'any', type: 'image/svg+xml', purpose: 'any maskable' }]);
  assert.match(read('public/icon.svg'), /viewBox="0 0 512 512"/);
});

test('Web export configures the manifest and scoped offline service worker', () => {
  const script = read('scripts/configure-pwa.mjs');
  const worker = read('public/sw.js');
  assert.match(script, /manifest\.webmanifest/);
  assert.match(script, /serviceWorker\.register\("\.\/sw\.js"\)/);
  assert.match(worker, /event\.request\.mode === 'navigate'/);
  assert.match(worker, /fetch\(event\.request\)/);
  assert.match(worker, /caches\.match\('\.\/'\)/);
  assert.match(worker, /gait-steps-pwa-v1/);
});

test('Pages workflow exports the shared app through the PWA post-processing script', () => {
  const workflow = read('../.github/workflows/publish-results.yml');
  assert.match(workflow, /npm run export:web/);
  assert.doesNotMatch(workflow, /expo-updates|eas update/i);
});
