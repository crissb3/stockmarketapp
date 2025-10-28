<script setup lang="ts">
import { ref, onMounted} from "vue";
import { portfolioApi } from "@/api/api";
import type { PortfolioTotal, Asset } from "@/types/portfolio";

const assets = ref<Asset[]>([])
const totals = ref<PortfolioTotal[]>([])
const latestAssets = ref<Asset[]>([])




onMounted(async ()=> {
    try {
        const [a, t, la] = await Promise.all([
            portfolioApi.getAssets(),
            portfolioApi.getTotals(),
            portfolioApi.getLatestAssets(),
        ]);
        assets.value = a;
        totals.value = t;
        latestAssets.value = la;
    } catch(error) {
        console.error(error);
    } 
});
</script>

<template>
<div class="text-black bg-amber-700 font-inter" v-for="a in assets">
    {{ a.symbol + ' - ' + a.value + a.currency}}
</div>
<div class="text-black bg-blue-400" v-for="t in totals">
    {{ t.totalValue + t.currency}}
</div>
</template>