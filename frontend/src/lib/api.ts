import type { Product } from "../components/ui/ProductCard/ProductCard";

export type Category = {
    id: string;
    name: string;
    slug: string;
    parent_id: string | null;
};

async function getJson<T>(url: string, signal?: AbortSignal): Promise<T> {
    const response = await fetch(url, {
        signal,
        headers: { Accept: "application/json" },
    });

    if (!response.ok) {
        throw new Error(`Ошибка API: ${response.status}`);
    }

    return response.json() as Promise<T>;
}

export function getCategories(signal?: AbortSignal) {
    return getJson<Category[]>("/api/v1/categories", signal);
}

export function getProducts(categoryId?: string, signal?: AbortSignal) {
    const query = categoryId
        ? `?category_id=${encodeURIComponent(categoryId)}`
        : "";

    return getJson<Product[]>(`/api/v1/products${query}`, signal);
}