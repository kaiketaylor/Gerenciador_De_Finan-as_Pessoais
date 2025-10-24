import { TxForm } from './tx-form'
import { TxTable } from './tx-table'

export const metadata = { title: 'Transações — Finanças Pro' }

export default function TransactionsPage(){
  return (
    <section className="grid md:grid-cols-3 gap-4">
      <div className="card p-5 md:col-span-1">
        <h2 className="text-xl font-semibold mb-3">Nova transação</h2>
        <TxForm />
      </div>
      <div className="card p-5 md:col-span-2">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-xl font-semibold">Transações</h2>
        </div>
        <TxTable />
      </div>
    </section>
  )
}
