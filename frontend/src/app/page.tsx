"use client";

import { useCallback, useEffect, useState } from "react";
import { Button } from "../components/ui/Button/Button";
import { Container } from "../components/ui/Container/Container";
import {
  ProductCard,
  type Product,
} from "../components/ui/ProductCard/ProductCard";
import { getCategories, getProducts, type Category } from "../lib/api";
import styles from "./page.module.scss";

export default function Home() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [selectedCategory, setSelectedCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const loadCatalog = useCallback(async (categoryId: string, signal: AbortSignal) => {
    setLoading(true);
    setError("");

    try {
      const [nextCategories, nextProducts] = await Promise.all([
        getCategories(signal),
        getProducts(categoryId || undefined, signal),
      ]);

      setCategories(nextCategories);
      setProducts(nextProducts);
    } catch (err) {
      if (err instanceof Error && err.name === "AbortError") return;

      setError("Не удалось загрузить каталог. Проверьте соединение и попробуйте ещё раз.");
    } finally {
      if (!signal.aborted) setLoading(false);
    }
  }, []);

  useEffect(() => {
    const controller = new AbortController();
    void loadCatalog(selectedCategory, controller.signal);

    return () => controller.abort();
  }, [loadCatalog, selectedCategory]);

  return (
      <main className={styles.page}>
        <header className={styles.header}>
          <Container className={styles.headerInner}>
            <a className={styles.brand} href="/" aria-label="Главная магазина">
              <span className={styles.brandMark}>м.</span>
              <span>тестовый магазин</span>
            </a>
            <span className={styles.headerNote}>Вещи для повседневной жизни</span>
          </Container>
        </header>

        <Container>
          <section className={styles.hero}>
            <p className={styles.eyebrow}>КОЛЛЕКЦИЯ МАГАЗИНА</p>
            <h1>Тестируем.<br />Хороший выбор.</h1>
            <p className={styles.intro}>
              Небольшая подборка товаров, которые могут вам понравиться.
            </p>
          </section>

          <section className={styles.catalog} aria-labelledby="catalog-title">
            <div className={styles.catalogHeading}>
              <div>
                <p className={styles.eyebrow}>НАШ АССОРТИМЕНТ</p>
                <h2 id="catalog-title">Каталог</h2>
              </div>
              <span className={styles.count}>
              {loading ? "Загружаем…" : `${products.length} товаров`}
            </span>
            </div>

            <div className={styles.filters} aria-label="Фильтр по категориям">
              <Button
                  variant="secondary"
                  active={selectedCategory === ""}
                  aria-pressed={selectedCategory === ""}
                  onClick={() => setSelectedCategory("")}
              >
                Все товары
              </Button>

              {categories
                  .filter((category) => category.slug !== "uncategorized")
                  .map((category) => (
                      <Button
                          key={category.id}
                          variant="secondary"
                          active={selectedCategory === category.id}
                          aria-pressed={selectedCategory === category.id}
                          onClick={() => setSelectedCategory(category.id)}
                      >
                        {category.name}
                      </Button>
                  ))}
            </div>

            {error ? (
                <div className={styles.message} role="alert">
                  <p>{error}</p>
                  <Button onClick={() => {
                    const controller = new AbortController();
                    void loadCatalog(selectedCategory, controller.signal);
                  }}>
                    Попробовать снова
                  </Button>
                </div>
            ) : loading ? (
                <div className={styles.message} role="status">
                  Загружаем товары…
                </div>
            ) : products.length === 0 ? (
                <div className={styles.message}>
                  В этой категории пока нет товаров.
                </div>
            ) : (
                <div className={styles.grid}>
                  {products.map((product) => (
                      <ProductCard key={product.id} product={product} />
                  ))}
                </div>
            )}
          </section>

          <footer className={styles.footer}>
            <span>тестовый магазин</span>
            <span><a href="https://t.me/kwadik" target="_blank">Kwadik</a></span>
          </footer>
        </Container>
      </main>
  );
}