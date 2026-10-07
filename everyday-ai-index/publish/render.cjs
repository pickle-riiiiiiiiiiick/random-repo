// Renders a slide deck HTML file to a LinkedIn-ready PDF (1080 x 1350 per page),
// and optionally each slide to PNG.
//
//   node render.cjs deck.html out.pdf [--png-dir dir] [--cover-png file.png]
//
// Needs Node with the `playwright` package and a Chromium it can launch
// (`npm i -g playwright && npx playwright install chromium`).

const path = require("path");
const fs = require("fs");

function loadPlaywright() {
  try {
    return require("playwright");
  } catch (_) {
    const { execSync } = require("child_process");
    const globalRoot = execSync("npm root -g").toString().trim();
    return require(path.join(globalRoot, "playwright"));
  }
}

async function main() {
  const args = process.argv.slice(2);
  const [input, output] = args;
  if (!input || !output) {
    console.error("usage: node render.cjs deck.html out.pdf [--png-dir dir] [--cover-png file.png]");
    process.exit(2);
  }
  const opt = (name) => {
    const i = args.indexOf(name);
    return i >= 0 ? args[i + 1] : null;
  };
  const pngDir = opt("--png-dir");
  const coverPng = opt("--cover-png");

  const { chromium } = loadPlaywright();
  const browser = await chromium.launch();
  const page = await browser.newPage({ viewport: { width: 1080, height: 1350 }, deviceScaleFactor: 1 });
  await page.goto("file://" + path.resolve(input), { waitUntil: "load" });
  await page.evaluate(() => document.fonts.ready);

  const missing = await page.evaluate(() =>
    ["Archivo", "Archivo Narrow", "Newsreader"].filter((f) => !document.fonts.check(`700 30px "${f}"`)));
  if (missing.length) {
    console.error("fonts failed to load: " + missing.join(", "));
    process.exit(1);
  }

  // Flag any text that spills outside its slide: a clipped headline is a broken post.
  const overflow = await page.evaluate(() => {
    const issues = [];
    document.querySelectorAll(".evd-post").forEach((post, i) => {
      const box = post.getBoundingClientRect();
      post.querySelectorAll("h1, p, li, figure, table, .evd-post__foot").forEach((el) => {
        const r = el.getBoundingClientRect();
        if (r.bottom > box.bottom + 1 || r.right > box.right + 1) issues.push(`slide ${i + 1}: <${el.tagName.toLowerCase()}> "${(el.textContent || "").slice(0, 40)}"`);
      });
      const body = post.querySelector(".evd-post__body");
      if (body && body.scrollHeight > body.clientHeight + 2) issues.push(`slide ${i + 1}: body content ${body.scrollHeight - body.clientHeight}px taller than the space left`);
    });
    return issues;
  });
  if (overflow.length) console.warn("WARNING overflow:\n  " + overflow.join("\n  "));

  await page.pdf({ path: output, width: "1080px", height: "1350px", printBackground: true, preferCSSPageSize: true });

  const slides = await page.$$(".evd-post");
  if (pngDir) {
    fs.mkdirSync(pngDir, { recursive: true });
    for (let i = 0; i < slides.length; i++) {
      await slides[i].screenshot({ path: path.join(pngDir, `slide-${String(i + 1).padStart(2, "0")}.png`) });
    }
  }
  if (coverPng && slides.length) await slides[0].screenshot({ path: coverPng });

  await browser.close();
  console.log(`${slides.length} slides -> ${output}`);
}

main().catch((e) => {
  console.error(e);
  process.exit(1);
});
