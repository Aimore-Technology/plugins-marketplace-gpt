#!/usr/bin/env node
// Optional local renderer. Uses an existing Playwright/Chromium installation;
// never installs dependencies, contacts a connector, uploads, or approves.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const {pathToFileURL} = require('node:url');

const hash = bytes => crypto.createHash('sha256').update(bytes).digest('hex');

async function main() {
  const args = process.argv.slice(2);
  const options = {};
  const keys = new Set(['html', 'html-sha256', 'version', 'out-dir', 'width', 'playwright-module', 'chromium']);
  for (let i = 0; i < args.length; i += 2) {
    const key = args[i].slice(2);
    if (!args[i].startsWith('--') || !keys.has(key) || options[key] !== undefined || !args[i + 1]) {
      throw new Error('Use --html FILE --html-sha256 DIGEST --version VERSION --out-dir NEW_DIR [--width 720] [--playwright-module INSTALLED_MODULE] [--chromium INSTALLED_EXECUTABLE]');
    }
    options[key] = args[i + 1];
  }
  if (!options.html || !/^[a-f0-9]{64}$/.test(options['html-sha256'] || '') || !options.version || !options['out-dir']) {
    throw new Error('Frozen HTML, SHA-256, content version and new output directory are required');
  }
  const source = fs.realpathSync(options.html);
  const bytes = fs.readFileSync(source);
  if (hash(bytes) !== options['html-sha256']) throw new Error('Frozen source digest mismatch');
  const html = new TextDecoder('utf-8', {fatal: true}).decode(bytes);
  if (!Buffer.from(html, 'utf8').equals(bytes)) throw new Error('HTML must round-trip as UTF-8 without changing bytes');
  const output = path.resolve(options['out-dir']);
  if (fs.existsSync(output)) throw new Error('Output directory exists; preserve previous versions');
  const width = options.width === undefined ? 720 : Number(options.width);
  if (!Number.isInteger(width) || width < 320 || width > 4096) throw new Error('Width must be an integer from 320 to 4096');
  let playwright;
  try { playwright = require(options['playwright-module'] || 'playwright'); }
  catch { throw new Error('Existing Playwright module unavailable; provide its installed path or use a supported host renderer. Nothing was installed.'); }
  const launch = {headless: true};
  if (options.chromium) launch.executablePath = fs.realpathSync(options.chromium);
  const browser = await playwright.chromium.launch(launch);
  try {
    const page = await browser.newPage({viewport: {width, height: 100}, deviceScaleFactor: 1, javaScriptEnabled: false, serviceWorkers: 'block'});
    page.setDefaultTimeout(15000);
    const blocked = [];
    const sourceURL = pathToFileURL(source).href;
    await page.route('**/*', route => {
      const request = route.request();
      const url = request.url();
      if ((url === sourceURL && request.isNavigationRequest() && request.frame() === page.mainFrame()) || url.startsWith('data:')) {
        return route.continue();
      }
      blocked.push(url);
      return route.abort();
    });
    await page.goto(sourceURL, {waitUntil: 'load'});
    await page.evaluate(() => document.fonts.ready);
    const missing = await page.evaluate(() => [...document.images].some(image => !image.complete || !image.naturalWidth));
    if (missing || blocked.length) throw new Error('Incomplete assets: freeze authorized images/fonts into this HTML as data URIs before rendering; no preview produced');
    const png = await page.screenshot({fullPage: true, animations: 'disabled'});
    if (blocked.length || !fs.readFileSync(source).equals(bytes)) throw new Error('Resource blocked or frozen source changed during render');
    const manifest = {
      content_version: options.version, source_html_sha256: hash(bytes), source_bytes: bytes.length,
      preview_png_sha256: hash(png), preview_bytes: png.length,
      width: png.readUInt32BE(16), height: png.readUInt32BE(20),
      renderer: 'playwright-chromium', browser_version: browser.version(),
      javascript_enabled: false, blocked_resources: [], completed: true,
      created_at: new Date().toISOString()
    };
    fs.mkdirSync(output, {recursive: false});
    fs.writeFileSync(path.join(output, 'frozen.html'), bytes, {flag: 'wx'});
    fs.writeFileSync(path.join(output, 'preview.png'), png, {flag: 'wx'});
    fs.writeFileSync(path.join(output, 'render-manifest.json'), JSON.stringify(manifest, null, 2) + '\n', {flag: 'wx'});
    console.log(JSON.stringify({status: 'RenderedForInspection', output_directory: output, ...manifest}));
  } finally { await browser.close(); }
}

main().catch(error => { console.error(JSON.stringify({status: 'NeedsCorrection', reason: error.message})); process.exitCode = 2; });
