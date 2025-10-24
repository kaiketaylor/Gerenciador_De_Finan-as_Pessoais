import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'Gerenciador de Finanças — Pro (Beta)',
  description: 'Aplicação profissional em Next.js para finanças pessoais.',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="pt-BR">
      <body>
        import Link from "next/link"

        <header className="border-b border-border">
          <div className="container py-3 flex items-center justify-between">
            <h1 className="text-lg font-semibold">Finanças <span className="text-primary">Pro</span></h1>
            <nav className="flex gap-2">
              <Link className="btn" href="/">Dashboard</Link>
              <Link className="btn" href="/app/transactions">Transações</Link>
              <Link className="btn" href="/app/budgets">Orçamentos</Link>
            </nav>
          </div>
        </header>
        <main className="container py-6">{children}</main>
        <footer className="container py-8 text-muted text-sm">
          Versão Beta • Armazenamento local (ainda sem backend). Estrutura pronta para Prisma/Postgres.
        </footer>
      </body>
    </html>
  )
}
