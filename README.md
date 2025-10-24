# Gerenciador de Finanças — Pro (Beta)

Estrutura **profissional** pronta para evoluir a um app full‑stack (Next.js + TypeScript + Tailwind + Prisma/Postgres).
Este repositório já traz padrões de projeto, pastas, scripts e páginas iniciais para **Dashboard**, **Transações** e **Orçamentos**.

## Stack
- Next.js (App Router), React 18, TypeScript
- TailwindCSS
- Prisma ORM (PostgreSQL)
- Vitest para testes
- Playwright (pré-configurado)
- ESLint + Prettier
- Docker Compose (serviço Postgres)

## Rodar local
```bash
pnpm i
cp .env.example .env.local   # edite se quiser usar Postgres local
pnpm dev
```
Abrir: http://localhost:3000

> **Sem DB:** por padrão, a versão Beta usa **localStorage** para transações. Conecte o Postgres e troque os handlers para Prisma conforme for avançando.

## Usar Postgres (opcional)
```bash
docker compose -f docker/compose.yml up -d
pnpm db:migrate
pnpm db:seed
```

## Estrutura de pastas
```
app/                 # páginas (App Router)
  app/transactions   # tela de transações (Beta: localStorage)
components/          # UI e componentes utilitários
domain/              # regras e schemas (Zod)
lib/                 # utilitários (money, store, auth futuramente)
prisma/              # schema e seeds
public/              # estáticos
```

## Próximos passos sugeridos
1. Substituir `app/api/v1/transactions` para usar Prisma.
2. Criar entidades `Category` e `Budget` no Prisma e migrar UI.
3. Implementar importador CSV (adapters/importers).
4. Autenticação (NextAuth) e autorização por usuário.
5. Testes E2E com Playwright nas jornadas críticas.
