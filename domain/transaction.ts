import { z } from 'zod'
export const TransactionSchema = z.object({
  id: z.string().uuid().optional(),
  date: z.string(), // ISO YYYY-MM-DD
  type: z.enum(['income','expense','transfer']).default('expense'),
  description: z.string().min(1),
  category: z.string().optional(),
  amountCents: z.number().int().nonnegative()
})
export type Transaction = z.infer<typeof TransactionSchema>
