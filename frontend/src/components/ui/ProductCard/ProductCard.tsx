"use client";

import { useState } from "react";
import styles from "./ProductCard.module.scss";

export type Product = {
    id: string;
    category_id: string;
    title: string;
    description: string | null;
    image_url: string | null;
    price: string;
    currency: string | null;
};

type ProductCardProps = {
    product: Product;
};

export function ProductCard({ product }: ProductCardProps) {
    const [imageFailed, setImageFailed] = useState(false);

    const price = new Intl.NumberFormat("ru-RU", {
        maximumFractionDigits: 2,
    }).format(Number(product.price));

    return (
        <article className={styles.card}>
            <div className={styles.image}>
                {product.image_url && !imageFailed ? (
                    // URL отдаёт FastAPI через прокси Next.js.
                    // eslint-disable-next-line @next/next/no-img-element
                    <img
                        src={product.image_url}
                        alt={product.title}
                        loading="lazy"
                        onError={() => setImageFailed(true)}
                    />
                ) : (
                    <div className={styles.placeholder} aria-label="Нет изображения">
                        <span>Фото товара</span>
                    </div>
                )}
            </div>

            <div className={styles.content}>
                <h2 className={styles.title}>{product.title}</h2>

                {product.description && (
                    <p className={styles.description}>{product.description}</p>
                )}

                <div className={styles.footer}>
                    <p className={styles.price}>
                        {price}
                        {product.currency ? ` ${product.currency}` : " ₽"}
                    </p>
                    <span className={styles.details}>Товар магазина</span>
                </div>
            </div>
        </article>
    );
}