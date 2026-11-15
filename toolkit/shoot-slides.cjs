// Renders each slide of comp/slides as a 1080x1350 JPG.
const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const p = await b.newPage({ viewport: { width: 1080, height: 1350 }, colorScheme: 'dark' });
  await p.goto('http://localhost:4180/__brag/slides/?s=1', { waitUntil: 'load' });
  const n = await p.evaluate(() => window.ready);
  for (let i = 1; i <= n; i++) {
    await p.goto(`http://localhost:4180/__brag/slides/?s=${i}`, { waitUntil: 'load' });
    await p.evaluate(() => window.ready);
    await p.screenshot({ path: `${process.argv[2]}/slide-${String(i).padStart(2, '0')}.jpg`, type: 'jpeg', quality: 92 });
  }
  console.log('slides', n);
  await b.close();
})();
