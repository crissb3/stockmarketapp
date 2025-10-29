<script setup lang="ts">
import { ref, onMounted } from "vue";
import { portfolioApi } from "@/api/api";
import type { PortfolioTotal, Asset } from "@/types/portfolio";

const assets = ref<Asset[]>([])
const totals = ref<PortfolioTotal[]>([])
const latestAssets = ref<Asset[]>([])
const totalProfit = ref<string | null>(null)




onMounted(async () => {
    try {
        // TODO: Bruk pinia for å slippe requests mot backend hver gang når data kun oppdateres 1 gang daglig
        const [a, t, la] = await Promise.all([
            portfolioApi.getAssets(),
            portfolioApi.getTotals(),
            portfolioApi.getLatestAssets(),
        ]);
        assets.value = a;
        totals.value = t;
        latestAssets.value = la;
        const sortedTotals = [...totals.value].sort(
            (a, b) => new Date(a.dateTime).getTime() - new Date(b.dateTime).getTime()
        )

        const firstTotalValue = sortedTotals[0]?.totalValue
        const latestTotalValue = sortedTotals[sortedTotals.length - 1]?.totalValue
        if (firstTotalValue && latestTotalValue) totalProfit.value = (latestTotalValue - firstTotalValue).toFixed(2);
    } catch (error) {
        console.error(error);
    }
});

function formatDate(date: string) {
    return new Date(date).toLocaleDateString('no-NO', {
        month: 'short',
        day: 'numeric',
        year: '2-digit',
    })
}
</script>

<template>
    <div class="flex flex-col items-center">
        <div class="p-4 font-bold text-4xl">
            <h1 class="py-2">Total profit</h1>
            <p :class="Number(totalProfit) > 0 ? 'text-green-500' : 'text-red-500'">{{ totalProfit }}</p>
        </div>
        <div class="flex flex-row gap-x-20">
            <table class="table-auto text-left">
                <thead class="border border-black">
                    <tr>
                        <th class="p-2">Total value</th>
                        <th class="p-2">Date</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(total, i) in totals.slice(0, 5)" :key="i" class="border border-black">
                        <td class="p-2">{{ total.totalValue + total.currency }}</td>
                        <td class="p-2">{{ formatDate(total.dateTime) }}</td>
                    </tr>
                </tbody>
            </table>
            <table class="table-auto text-left border border-black">
                <thead>
                    <tr>
                        <th class="p-2">Symbol</th>
                        <th class="p-2">Shares</th>
                        <th class="p-2">Latest Close</th>
                        <th class="p-2">Value</th>
                        <th class="p-2">Currency</th>
                        <th class="p-2">Updated</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-for="(asset, i) in latestAssets" :key="i" class="border border-black">
                        <td class="p-2">{{ asset.symbol }}</td>
                        <td class="p-2">{{ asset.shares }}</td>
                        <td class="p-2">{{ asset.latestClose }}</td>
                        <td class="p-2">{{ asset.value }}</td>
                        <td class="p-2">{{ asset.currency }}</td>
                        <td class="p-2">{{ formatDate(asset.dateTime) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</template>