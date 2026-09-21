// Build 2 was fingerprinted from Windows files. Restore only the exact known
// config bytes after Git's LF checkout; never override a native runtime hash.
const fs = require('node:fs');
const crypto = require('node:crypto');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const hash = value => crypto.createHash('sha1').update(value).digest('hex');
const contracts = [
  ['.gitignore', 'c3f1927251ca5385fef89328bf01b6bb240941af', '1ad48a15cd3dd8bef674da678a0ac7f107afab80', s => s.replace(/\n/g, '\r\n')],
  ['eas.json', 'b14cf15ac6ee2741dd7e2d74235044a1d29a046e', '7a378f6ebb71e73acbcd084afcfc4f32f4994591',
    s => s.split('\n').map((line,i,lines) => i === lines.length-1 ? line : line + (/^  "cli":|^    "preview":/.test(line) ? '\n' : '\r\n')).join('')],
];
for (const [file, canonicalHash, installedHash, restore] of contracts) {
  const target = path.join(root,file), current=fs.readFileSync(target,'utf8');
  const canonical=current.replace(/\r\n/g,'\n');
  if (hash(canonical)!==canonicalHash) {
    console.log(`${file}: content changed; retain normal fingerprint compatibility checks.`);
    continue;
  }
  const restored=restore(canonical);
  if(hash(restored)!==installedHash)throw new Error(`Unexpected compatibility bytes for ${file}`);
  fs.writeFileSync(target,restored);
  console.log(`${file}: preserved build 2 config bytes.`);
}
