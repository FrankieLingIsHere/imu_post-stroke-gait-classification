import { createServer } from 'node:http'
import { readFile, stat, mkdir, rm } from 'node:fs/promises'
import { extname, join, normalize, resolve } from 'node:path'
import { chromium } from 'playwright-chromium'

const [buildDirectory, outputDirectory, slideCount = '18'] = process.argv.slice(2)
if (!buildDirectory || !outputDirectory) {
  throw new Error('Usage: node scripts/capture-slides.mjs <build-dir> <output-dir> [slide-count]')
}

const root = resolve(buildDirectory)
const output = resolve(outputDirectory)
const contentTypes = {
  '.css': 'text/css',
  '.html': 'text/html',
  '.js': 'text/javascript',
  '.json': 'application/json',
  '.png': 'image/png',
  '.svg': 'image/svg+xml',
  '.woff2': 'font/woff2',
}

const server = createServer(async (request, response) => {
  try {
    const requestPath = decodeURIComponent(new URL(request.url, 'http://127.0.0.1').pathname)
    let filePath = normalize(join(root, requestPath))
    if (!filePath.startsWith(root)) throw new Error('Invalid path')
    try {
      if ((await stat(filePath)).isDirectory()) filePath = join(filePath, 'index.html')
    } catch {
      filePath = join(root, 'index.html')
    }
    response.setHeader('Content-Type', contentTypes[extname(filePath)] || 'application/octet-stream')
    response.end(await readFile(filePath))
  } catch (error) {
    response.statusCode = 404
    response.end(String(error))
  }
})

await rm(output, { recursive: true, force: true })
await mkdir(output, { recursive: true })
await new Promise(resolveListen => server.listen(0, '127.0.0.1', resolveListen))
const { port } = server.address()
const browser = await chromium.launch({ headless: true })

try {
  const page = await browser.newPage({ viewport: { width: 1280, height: 720 } })
  const overflows = []
  for (let slide = 1; slide <= Number(slideCount); slide += 1) {
    await page.goto(`http://127.0.0.1:${port}/${slide}`, { waitUntil: 'networkidle' })
    await page.waitForTimeout(200)
    const overflow = await page.locator('.slidev-layout').evaluateAll(elements => {
      const centreX = window.innerWidth / 2
      const centreY = window.innerHeight / 2
      const element = elements.find(candidate => {
        const rect = candidate.getBoundingClientRect()
        return rect.left <= centreX && rect.right >= centreX && rect.top <= centreY && rect.bottom >= centreY
      })
      if (!element) throw new Error('Could not identify the active slide layout')
      const table = element.querySelector('table')
      const footer = element.querySelector('.source-footer')
      return {
        clientHeight: element.clientHeight,
        scrollHeight: element.scrollHeight,
        clientWidth: element.clientWidth,
        scrollWidth: element.scrollWidth,
        tableClass: table?.className || null,
        tableFontSize: table ? getComputedStyle(table).fontSize : null,
        footerPosition: footer ? getComputedStyle(footer).position : null,
        footerBottom: footer ? getComputedStyle(footer).bottom : null,
      }
    })
    if (overflow.scrollHeight > overflow.clientHeight || overflow.scrollWidth > overflow.clientWidth) {
      overflows.push({ slide, ...overflow })
    }
    await page.screenshot({ path: join(output, `${String(slide).padStart(2, '0')}.png`) })
  }

  const phone = await browser.newPage({ viewport: { width: 390, height: 844 } })
  await phone.goto(`http://127.0.0.1:${port}/1`, { waitUntil: 'networkidle' })
  await phone.waitForTimeout(200)
  await phone.screenshot({ path: join(output, 'phone-slide-01.png') })

  console.log(JSON.stringify({ slides: Number(slideCount), overflows }, null, 2))
} finally {
  await browser.close()
  await new Promise(resolveClose => server.close(resolveClose))
}
