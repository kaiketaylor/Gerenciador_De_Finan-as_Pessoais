'use client'
import { useEffect, useMemo, useState } from 'react'
import { store, TxRecord } from '@/lib/store'
import { currency } from '@/lib/money'

export function TxTable(){
  const [txs, setTxs] = useState<TxRecord[]>(store.list())
  useEffect(()=>store.subscribe(()=>setTxs(store.list())),[])

  const rows = useMemo(()=>txs.sort((a,b)=>a.date.localeCompare(b.date)),[txs])

  function remove(id: string){ store.remove(id) }

  return (
    <div className="overflow-x-auto">
      <table className="table">
        <thead><tr><th>Data</th><th>Tipo</th><th>Descrição</th><th>Categoria</th><th className="text-right">Valor</th><th></th></tr></thead>
        <tbody>
          {rows.map(tx => (
            <tr key={tx.id}>
              <td>{tx.date}</td>
              <td>{tx.type==='income'?'Receita':'Despesa'}</td>
              <td>{tx.description}</td>
              <td>{tx.category}</td>
              <td className="text-right">{currency(tx.amountCents * (tx.type==='income'?1:-1))}</td>
              <td className="text-right"><button className="btn" onClick={()=>remove(tx.id)}>Remover</button></td>
            </tr>
          ))}
          {rows.length===0 && <tr><td colSpan={6} className="text-center text-muted py-6">Nenhuma transação ainda.</td></tr>}
        </tbody>
      </table>
    </div>
  )
}
