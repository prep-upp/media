// Serves the built site (dist/) + the composition (/__brag/) on one origin.
const http = require('http'), fs = require('fs'), path = require('path');
const DIST = path.resolve(__dirname, '../../dist'), COMP = path.resolve(__dirname, 'comp');
const TYPES = { '.html': 'text/html; charset=utf-8', '.js': 'text/javascript', '.css': 'text/css', '.svg': 'image/svg+xml', '.png': 'image/png', '.json': 'application/json', '.woff2': 'font/woff2' };
http.createServer((req, res) => {
  let u = decodeURIComponent(req.url.split('?')[0]);
  let root = DIST;
  if (u.startsWith('/__brag/')) { root = COMP; u = u.slice(7); }
  let f = path.join(root, u);
  if (!f.startsWith(root)) { res.writeHead(403); return res.end(); }
  if (fs.existsSync(f) && fs.statSync(f).isDirectory()) f = path.join(f, 'index.html');
  if (!fs.existsSync(f) && fs.existsSync(f + '.html')) f = f + '.html';
  if (!fs.existsSync(f)) { res.writeHead(404); return res.end('nf'); }
  res.writeHead(200, { 'content-type': TYPES[path.extname(f)] || 'application/octet-stream' });
  fs.createReadStream(f).pipe(res);
}).listen(4180, () => console.log('on 4180'));
