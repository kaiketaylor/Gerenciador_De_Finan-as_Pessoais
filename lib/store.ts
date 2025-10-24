function uuid() {
  if (typeof globalThis !== 'undefined' && globalThis.crypto && 'randomUUID' in globalThis.crypto) {
    return globalThis.crypto.randomUUID();
  }
  // Fallback simples
  return 'id-' + Math.random().toString(16).slice(2) + '-' + Date.now().toString(16);
}

export type TxInput = {
  date: string
  type: 'income' | 'expense'
  description: string
  category?: string
  amount: number // in BRL
}

export type TxRecord = {
  id: string
  date: string
  type: 'income' | 'expense'
  description: string
  category: string
  amountCents: number // always positive
}

type Listener = () => void

class LocalStore {
  private key = 'financas.txs.v1'
  private listeners: Listener[] = []

  list(): TxRecord[] {
    if (typeof localStorage === 'undefined') return []
    const raw = localStorage.getItem(this.key)
    if(!raw) return []
    try { return JSON.parse(raw) } catch { return [] }
  }
  save(list: TxRecord[]){ if (typeof localStorage !== 'undefined') localStorage.setItem(this.key, JSON.stringify(list)) }
  subscribe(fn: Listener){ this.listeners.push(fn); return ()=>{ this.listeners = this.listeners.filter(x=>x!==fn) } }
  emit(){ this.listeners.forEach(fn=>fn()) }

  create(input: TxInput){
    const list = this.list()
    const rec: TxRecord = {
      id: uuid(),
      date: input.date,
      type: input.type,
      description: input.description,
      category: input.category ?? '',
      amountCents: Math.round(Math.abs(input.amount) * 100),
    }
    list.push(rec); this.save(list); this.emit()
  }
  remove(id: string){
    const list = this.list().filter(x=>x.id!==id)
    this.save(list); this.emit()
  }
  clear(){ this.save([]); this.emit() }
  seed(){
    const today = new Date()
    const month = today.toISOString().slice(0,7)
    const examples: TxRecord[] = [
      { id: uuid(), date: f(month, 2), type:'income', description:'Salário', category:'Renda', amountCents: 550000 },
      { id: uuid(), date: f(month, 3), type:'expense', description:'Aluguel', category:'Moradia', amountCents: 170000 },
      { id: uuid(), date: f(month, 5), type:'expense', description:'Mercado', category:'Alimentação', amountCents: 82000 },
      { id: uuid(), date: f(month, 6), type:'expense', description:'Transporte', category:'Transporte', amountCents: 30000 },
      { id: uuid(), date: f(month, 10), type:'income', description:'Freela', category:'Renda', amountCents: 120000 },
    ]
    this.save(examples); this.emit()
  }
}
function f(month: string, day: number){ return `${month}-${String(day).padStart(2,'0')}` }
export const store = new LocalStore()
