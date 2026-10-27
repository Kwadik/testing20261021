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
export type OrderItemInput = {
    product_id: string;
    quantity: number;
};

export type OrderCreateInput = {
    customer_name: string;
    customer_contact: string;
    items: OrderItemInput[];
};

export type CreatedOrder = {
    id: string;
    customer_name: string;
    customer_contact: string;
    status: string;
    total_amount: string;
    currency: string;
    created_at: string;
    items: {
        id: string;
        product_id: string;
        product_title: string;
        quantity: number;
        unit_price: string;
    }[];
};

export async function createOrder(data: OrderCreateInput): Promise<CreatedOrder> {
    const response = await fetch("/api/v1/orders", {
        method: "POST",
        headers: {
            Accept: "application/json",
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        let message = `Ошибка оформления заказа: ${response.status}`;

        try {
            const body = await response.json();
            if (typeof body.detail === "string") {
                message = body.detail;
            }
        } catch {
            // Используем сообщение по умолчанию, если ответ не JSON.
        }

        throw new Error(message);
    }

    return response.json() as Promise<CreatedOrder>;
}
