import { NextResponse } from 'next/server'
// TODO: trocar por acesso real via Prisma após conectar o DB
let mem: any[] = []
export async function GET(){ return NextResponse.json(mem) }
export async function POST(req: Request){
  const body = await req.json()
  const rec = { id: crypto.randomUUID(), ...body }
  mem.push(rec)
  return NextResponse.json(rec, { status: 201 })
}
