import axios from "axios";
import type { SearchResponse } from "../types/article";

const API = axios.create({
    baseURL: "http://127.0.0.1:8000",
});

export async function searchNews(query: string) {
    const response = await API.post<SearchResponse>("/search", {
        query,
    });

    return response.data;
}
