// Проверка всех формул банка тем же KaTeX, что во фронтенде: node katex_check.cjs bank.json
const katex = require('/app/node_modules/katex');
const fs = require('fs');
const bank = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
let bad = 0, total = 0;
const seen = new Set();
for (const e of bank) {
  for (const field of ['condition', 'solution']) {
    const text = e[field] || '';
    const re = /\$\$([\s\S]+?)\$\$|\$([^$]+?)\$/g;
    let m;
    while ((m = re.exec(text))) {
      const tex = m[1] || m[2];
      total++;
      try { katex.renderToString(tex, { throwOnError: true, displayMode: !!m[1] }); }
      catch (err) {
        bad++;
        const key = e.template + ':' + err.message.slice(0, 60);
        if (!seen.has(key)) { seen.add(key); console.log(e.external_id, e.template, field, '|', tex.slice(0, 120), '|', err.message.slice(0, 120)); }
      }
    }
  }
}
console.log('формул:', total, 'ошибок:', bad);
