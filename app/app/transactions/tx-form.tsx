'use client'
import { useState } from 'react'
import { store, TxInput } from '@/lib/store'

export function TxForm(){
  const [form, setForm] = useState<TxInput>({
    date: new Date().toISOString().slice(0,10),
    type: 'expense',
    description: '',
    category: '',
    amount: 0
  })

  function onSubmit(e: React.FormEvent){
    e.preventDefault()
    store.create(form)
    setForm({ ...form, description: '', amount: 0 })
  }

  return (
    <form onSubmit={onSubmit} className="grid gap-2">
      <label>Data
        <input className="input" type="date" value={form.date} onChange={e=>setForm({...form, date:e.target.value})} required />
      </label>
      <label>Tipo
        <select className="input" value={form.type} onChange={e=>setForm({...form, type: e.target.value as any})}>
          <option value="income">Receita</option>
          <option value="expense">Despesa</option>
        </select>
      </label>
      <label>Descrição
        <input className="input" value={form.description} onChange={e=>setForm({...form, description:e.target.value})} placeholder="Ex.: Mercado, Aluguel..." required />
      </label>
      <label>Categoria
        <input className="input" value={form.category} onChange={e=>setForm({...form, category:e.target.value})} placeholder="Ex.: Alimentação" />
      </label>
      <label>Valor (BRL)
        <input className="input" type="number" step="0.01" min="0" value={form.amount} onChange={e=>setForm({...form, amount: Number(e.target.value)})} required />
      </label>
      <div className="flex gap-2 pt-2">
        <button className="btn btn-primary" type="submit">Adicionar</button>
        <button className="btn" type="button" onClick={()=>store.seed()}>Popular demo</button>
        <button className="btn" type="button" onClick={()=>store.clear()}>Limpar dados</button>
      </div>
    </form>
  )
}
