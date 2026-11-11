---
name: auditoria-de-seguranca
description: Faz uma auditoria de segurança do código de uma pasta com a skill security-audit da Cloudflare, sem mudar nenhum arquivo, e explica em português simples cada falha confirmada, da mais grave para a menos grave, com arquivo, problema, como corrigir e onde ficou o relatório. Use quando o usuário pedir auditoria de segurança, procurar falhas ou brechas no código.
---

# Auditoria de segurança

Responda em português simples. **Não mude nenhum arquivo do projeto.**

## Antes de começar
- Pergunte qual pasta auditar, se não estiver claro.
- Precisa da skill `security-audit` (github.com/cloudflare/security-audit-skill). Instalação: `npx skills add https://github.com/cloudflare/security-audit-skill --skill security-audit -g -a claude-code -y`. O `npx skills` precisa do Node.js 22.20 ou mais novo: se faltar, mostre o comando de instalar o Node antes (no Windows: `winget install OpenJS.NodeJS.LTS`) e espere o OK.
- Se ela não puder ser instalada, ofereça usar as skills de segurança que já existirem (ex.: `security-and-hardening`, `/security-review`).

## No fim
Explique cada falha **confirmada**, da mais grave para a menos grave: o arquivo, o problema e como corrigir. Diga onde ficou o relatório completo. Não trate suspeita como falha confirmada.
