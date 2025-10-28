import axios from "axios";

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    }
});

export const portfolioApi = {
    getAssets: async () => {
        const res = await api.get("/portfolio/assets");
        return res.data;
    },

    getLatestAssets: async () => {
        const res = await api.get("/portfolio/latest");
        return res.data;
    },

    getTotals: async () => {
        const res = await api.get("/portfolio/totals");
        return res.data;
    },
}