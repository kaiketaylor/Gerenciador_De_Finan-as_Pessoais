import Link from 'next/link'
import { Summary } from './summary'

export default function Page() {
  return (
    <section className="grid md:grid-cols-3 gap-4">
      <div className="card p-5 md:col-span-2">
        <h2 className="text-xl font-semibold mb-3">Resumo</h2>
        <Summary />
      </div>
      <div className="card p-5">
        <h2 className="text-xl font-semibold mb-3">Ações rápidas</h2>
        <ul className="list-disc ms-5 space-y-2">
          <li><Link className="underline" href="/app/transactions">Adicionar transação</Link></li>
          <li><Link className="underline" href="/app/transactions">Importar CSV</Link></li>
          <li><Link className="underline" href="/app/budgets">Criar orçamento</Link></li>
        </ul>
      </div>
    </section>
  )
}
