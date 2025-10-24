'use client'
import { useEffect, useMemo, useState } from 'react'
import { store } from '@/lib/store'
import { currency } from '@/lib/money'

export function Summary(){
  const [txs, setTxs] = useState(store.list())
  useEffect(()=>store.subscribe(()=>setTxs(store.list())),[])

  const {income, expense, balance} = useMemo(()=>{
    let i=0, e=0
    for(const t of txs){
      if(t.type==='income') i+=t.amountCents
      else e+=t.amountCents
    }
    return { income:i, expense:e, balance: i - e }
  },[txs])

  return (
    <div className="grid grid-cols-3 gap-3">
      <div className="card p-4">
        <p className="text-muted text-sm">Receitas</p>
        <p className="text-2xl font-semibold">{currency(income)}</p>
      </div>
      <div className="card p-4">
        <p className="text-muted text-sm">Despesas</p>
        <p className="text-2xl font-semibold">{currency(expense)}</p>
      </div>
      <div className="card p-4">
        <p className="text-muted text-sm">Saldo</p>
        <p className="text-2xl font-semibold">{currency(balance)}</p>
      </div>
    </div>
  )
}
