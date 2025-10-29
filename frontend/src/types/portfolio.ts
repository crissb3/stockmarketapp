export interface PortfolioTotal {
    id: number
    dateTime: string
    currency: string
    totalValue: number
}

export interface Asset {
    id: number
    dateTime: string
    symbol: string
    latestClose: number
    shares: number
    value: number
    currency: string
}