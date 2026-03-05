#!/usr/bin/env node
/**
 * Infographic Screenshot Tool
 * Takes an HTML file and produces a high-DPI PNG screenshot.
 *
 * Usage:
 *   node screenshot.js <input.html> <output.png> [scaleFactor] [viewportWidth]
 *
 * Defaults: scaleFactor=3, viewportWidth=750
 *
 * Requires: playwright (will attempt to locate via npx cache or global install)
 */

const path = require("path");
const fs = require("fs");

async function findPlaywright() {
  // Try direct require first
  try { return require("playwright"); } catch {}

  // Search npx cache
  const { execSync } = require("child_process");
  try {
    const dirs = fs.readdirSync(path.join(process.env.HOME, ".npm/_npx"));
    for (const dir of dirs) {
      const candidate = path.join(process.env.HOME, ".npm/_npx", dir, "node_modules/playwright");
      if (fs.existsSync(candidate)) {
        return require(candidate);
      }
    }
  } catch {}

  // Install via npx as last resort
  console.error("Playwright not found. Run: npx playwright install chromium");
  process.exit(1);
}

(async () => {
  const args = process.argv.slice(2);
  if (args.length < 2) {
    console.error("Usage: node screenshot.js <input.html> <output.png> [scaleFactor] [viewportWidth]");
    process.exit(1);
  }

  const inputHtml = path.resolve(args[0]);
  const outputPng = path.resolve(args[1]);
  const scaleFactor = parseInt(args[2] || "3", 10);
  const viewportWidth = parseInt(args[3] || "750", 10);

  if (!fs.existsSync(inputHtml)) {
    console.error(`File not found: ${inputHtml}`);
    process.exit(1);
  }

  const pw = await findPlaywright();
  const browser = await pw.chromium.launch();
  const ctx = await browser.newContext({
    viewport: { width: viewportWidth, height: 600 },
    deviceScaleFactor: scaleFactor,
  });
  const page = await ctx.newPage();
  await page.goto(`file://${inputHtml}`, { waitUntil: "networkidle" });
  await page.locator("body").screenshot({ path: outputPng, type: "png" });

  const { width, height } = await page.locator("body").boundingBox();
  console.log(`✅ ${outputPng}`);
  console.log(`   ${width * scaleFactor}×${Math.round(height * scaleFactor)}px (${scaleFactor}x, ${(fs.statSync(outputPng).size / 1024).toFixed(0)}KB)`);

  await browser.close();
})();
