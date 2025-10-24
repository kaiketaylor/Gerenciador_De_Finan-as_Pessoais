import { PrismaClient } from '@prisma/client'
const prisma = new PrismaClient()

async function main(){
  const user = await prisma.user.upsert({
    where: { email: 'demo@local' },
    create: { email: 'demo@local', name: 'Demo' },
    update: {}
  })
  const acc = await prisma.account.create({
    data: { userId: user.id, name:'Carteira', type:'wallet', currency:'BRL' }
  })
  await prisma.transaction.createMany({
    data: [
      { userId: user.id, accountId: acc.id, type:'income', amountCents: 500000, description:'Salário', category:'Renda', date: new Date() },
      { userId: user.id, accountId: acc.id, type:'expense', amountCents: 120000, description:'Aluguel', category:'Moradia', date: new Date() },
    ]
  })
}

main().catch(e=>{ console.error(e); process.exit(1) }).finally(()=>prisma.$disconnect())
