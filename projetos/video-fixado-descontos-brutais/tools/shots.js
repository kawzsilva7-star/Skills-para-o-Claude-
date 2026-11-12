const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 430, height: 900 }, deviceScaleFactor: 2 });
  await p.goto('file:///home/user/descontos_brutais.br/docs/index.html');
  await p.waitForTimeout(6000);
  await p.evaluate(() => document.querySelectorAll('details').forEach((d,i)=>{ if(i===0) d.open = true; }));
  const info = await p.evaluate(() => {
    const r = s => [...document.querySelectorAll(s)].slice(0,12).map(e => ({t:(e.innerText||'').trim().slice(0,50), y: Math.round(e.getBoundingClientRect().top + scrollY), h: Math.round(e.getBoundingClientRect().height)}));
    return { h2: r('h2'), botoes: r('.botao'), summary: r('summary'), itens: r('.item'), total: document.documentElement.scrollHeight,
      broken: [...document.images].filter(i=>!i.naturalWidth).length, imgs: document.images.length };
  });
  console.log(JSON.stringify(info));
  await p.screenshot({ path: 'public/shots/site-full.png', fullPage: true });
  await b.close();
})();
