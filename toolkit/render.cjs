// usage: node render.cjs stills <outdir> t1 t2 ...   |   node render.cjs video <out.mp4>
const { chromium } = require('playwright');
const { spawn } = require('child_process');
const FPS = 30, DUR = Number(process.env.DUR || 21), PAGE = process.env.PAGE || '/__brag/';
// BEATMAP=file.json: the song's real beat times (s, from the sound's start). Composition beat k (k * COMPBEAT s)
// is shown exactly at real beat k, linear in between, so every cut lands on the song's beat.
const COMPBEAT = Number(process.env.COMPBEAT || 0.5);
const BM = process.env.BEATMAP ? JSON.parse(require('fs').readFileSync(process.env.BEATMAP, 'utf8')) : null;
function compT(tr) {
  if (!BM) return tr;
  let k = 0; while (k < BM.length - 2 && BM[k + 1] <= tr) k++;
  return COMPBEAT * (k + (tr - BM[k]) / (BM[k + 1] - BM[k]));
}

(async () => {
  const [mode, out, ...rest] = process.argv.slice(2);
  const b = await chromium.launch({ executablePath: '/opt/pw-browsers/chromium' });
  const ctx = await b.newContext({ viewport: { width: 540, height: 960 }, deviceScaleFactor: 2, colorScheme: 'dark', reducedMotion: 'no-preference' });
  await ctx.addInitScript(() => { try { localStorage.setItem('theme', 'dark'); } catch (e) {} });
  const p = await ctx.newPage();
  p.on('pageerror', (e) => console.error('pageerror', e.message));
  await p.goto('http://localhost:4180' + PAGE, { waitUntil: 'load', timeout: 60000 });
  await p.evaluate(() => window.ready);

  if (mode === 'stills') {
    for (const t of rest.map(Number)) {
      await p.evaluate((t) => window.render(t), Math.max(0, compT(t)));
      await p.screenshot({ path: `${out}/s-${t.toFixed(2)}.png` });
    }
  } else {
    const ff = spawn('ffmpeg', ['-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', String(FPS), '-c:v', 'png', '-i', '-',
      '-c:v', 'libx264', '-preset', 'slow', '-crf', '16', '-pix_fmt', 'yuv420p', '-r', String(FPS), out], { stdio: ['pipe', 'inherit', 'inherit'] });
    const N = FPS * DUR, FROM = Number(process.env.FROM || 0), TO = Number(process.env.TO || N);
    for (let i = FROM; i < TO; i++) {
      await p.evaluate((t) => window.render(t), Math.max(0, compT(i / FPS)));
      const buf = await p.screenshot({ type: 'png' });
      if (!ff.stdin.write(buf)) await new Promise((r) => ff.stdin.once('drain', r));
      if (i % 60 === 0) console.log(`frame ${i}/${N}`);
    }
    ff.stdin.end();
    await new Promise((r) => ff.on('close', r));
  }
  await b.close();
})();
