"use client";

import { useState } from "react";
import { Button } from "../Button/Button";
import styles from "./ProductCard.module.scss";

export type Product = {
    id: string;
    category_id: string;
    title: string;
    description: string | null;
    image_url: string | null;
    price: string | null;
    currency: string | null;
};

type ProductCardProps = {
    product: Product;
    onAddToCart: (product: Product) => void;
};

export function ProductCard({ product, onAddToCart }: ProductCardProps) {
    const [imageFailed, setImageFailed] = useState(false);

    const currency = product.currency?.trim() || "RUB";

    const hasPrice =
        product.price !== null &&
        product.price.trim() !== "" &&
        Number.isFinite(Number(product.price)) &&
        Number(product.price) >= 0;

    const price = hasPrice
        ? new Intl.NumberFormat("ru-RU", {
            maximumFractionDigits: 2,
        }).format(Number(product.price))
        : null;

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
                    <div className={styles.details}>
                        <p className={styles.price}>
                            {price !== null
                                ? `${price} ${currency === "RUB" ? "₽" : currency}`
                                : "Цена не указана"}
                        </p>
                        <span className={styles.someLabel}>Товар магазина</span>
                    </div>
                    <div className={styles.buttonWrapper}>
                        <Button className={styles.submitButton} disabled={!hasPrice} onClick={() => onAddToCart(product)}>В корзину</Button>
                    </div>
                </div>
            </div>
        </article>
    );
}