export function currency(cents: number, locale='pt-BR', currency='BRL'){
  const value = (cents/100)
  return new Intl.NumberFormat(locale,{ style:'currency', currency }).format(value)
}
