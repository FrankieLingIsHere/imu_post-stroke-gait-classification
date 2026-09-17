import { readFile, writeFile, stat } from 'node:fs/promises';
import { resolve } from 'node:path';

const output = resolve(process.argv[2] ?? 'dist/web');
const indexPath = resolve(output, 'index.html');
await stat(indexPath);
let html = await readFile(indexPath, 'utf8');
if (!html.includes('manifest.webmanifest')) {
  html = html.replace('</head>', '  <link rel="manifest" href="./manifest.webmanifest" />\n  <meta name="theme-color" content="#176B62" />\n  <link rel="icon" href="./icon.svg" type="image/svg+xml" />\n</head>');
}
if (!html.includes("serviceWorker.register")) {
  html = html.replace('</body>', '  <script>if ("serviceWorker" in navigator) window.addEventListener("load", () => navigator.serviceWorker.register("./sw.js"));</script>\n</body>');
}
await writeFile(indexPath, html);
