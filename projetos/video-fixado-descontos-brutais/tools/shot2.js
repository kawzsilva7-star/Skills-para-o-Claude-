const { chromium } = require('playwright');
(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width: 430, height: 760 }, deviceScaleFactor: 2 });
  await p.goto('file:///home/user/descontos_brutais.br/docs/index.html');
  await p.waitForTimeout(5000);
  await p.screenshot({ path: 'tmp/pagina-whatsapp.png' });
  await b.close();
})();
