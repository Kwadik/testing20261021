"use client";

import { useCallback, useEffect, useState, type FormEvent } from "react";
import { Button } from "../components/ui/Button/Button";
import { Container } from "../components/ui/Container/Container";
import {
  ProductCard,
  type Product,
} from "../components/ui/ProductCard/ProductCard";
import { getCategories, getProducts, createOrder, type Category } from "../lib/api";
import styles from "./page.module.scss";

type TelegramUser = {
  first_name?: string;
  last_name?: string;
  username?: string;
};

export default function Home() {
  const [categories, setCategories] = useState<Category[]>([]);
  const [products, setProducts] = useState<Product[]>([]);
  const [cart, setCart] = useState<Record<string, { product: Product; quantity: number }>>({});
  const [selectedCategory, setSelectedCategory] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [customerName, setCustomerName] = useState("");
  const [customerContact, setCustomerContact] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [orderError, setOrderError] = useState("");
  const [orderSuccess, setOrderSuccess] = useState("");

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

  useEffect(() => {
    const user = window.Telegram?.WebApp?.initDataUnsafe?.user as
        | TelegramUser
        | undefined;

    if (!user) return;

    const fullName = [user.first_name, user.last_name]
        .filter((part) => part?.trim())
        .join(" ");

    if (fullName) {
      setCustomerName((current) =>
          current.trim() ? current : fullName
      );
    }

    if (user.username) {
      setCustomerContact((current) =>
          current.trim() ? current : `@${user.username}`
      );
    }
  }, []);

  async function submitOrder(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (submitting || Object.keys(cart).length === 0) return;

    setSubmitting(true);
    setOrderError("");
    setOrderSuccess("");

    try {
      const order = await createOrder({
        customer_name: customerName.trim(),
        customer_contact: customerContact.trim(),
        items: Object.values(cart).map(({ product, quantity }) => ({
          product_id: product.id,
          quantity,
        })),
      });

      setCart({});
      setCustomerName("");
      setCustomerContact("");
      setOrderSuccess(
        `Заказ успешно создан. Номер заказа: ${order.id}. Сумма: ${order.total_amount} ${order.currency}.`,
      );
    } catch (err) {
      setOrderError(
        err instanceof Error ? err.message : "Не удалось оформить заказ. Попробуйте ещё раз.",
      );
    } finally {
      setSubmitting(false);
    }
  }

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
              <div className={styles.counters}>
                <span className={styles.count}>{loading ? "Загружаем…" : `Товаров: ${products.length}`}</span>
                <span className={styles.count}>В корзине: {Object.values(cart).reduce((sum, entry) => sum + entry.quantity, 0)}</span>
              </div>
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
                      <ProductCard
                          key={product.id}
                          product={product}
                          onAddToCart={(item) => setCart((current) => ({
                            ...current,
                            [item.id]: {
                              product: item,
                              quantity: (current[item.id]?.quantity ?? 0) + 1,
                            },
                          }))}
                      />
                  ))}
                </div>
            )}
          </section>

  
        <section className={styles.cart} aria-labelledby="cart-title">
          <div className={styles.cartHeading}>
            <div>
              <p className={styles.eyebrow}>ВАШ ВЫБОР</p>
              <h2 id="cart-title">Корзина</h2>
            </div>
            <span className={styles.count}>
              Товаров: {Object.values(cart).reduce((sum, entry) => sum + entry.quantity, 0)}
            </span>
          </div>

          {Object.values(cart).length === 0 ? (
            <div className={styles.message}>
              Корзина пока пуста. Добавьте товары из каталога.
            </div>
          ) : (
            <>
              <ul className={styles.cartList}>
                {Object.values(cart).map(({ product, quantity }) => {
                  const price = Number(product.price);
                  const money = (value: number) =>
                    new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 }).format(value);
                  const currency = product.currency?.trim() || "RUB";

                  return (
                    <li className={styles.cartItem} key={product.id}>
                      <div className={styles.cartProduct}>
                        <strong>{product.title}</strong>
                        <span>{money(price)}{currency === "RUB" ? " ₽" : ` ${currency}`} за шт.</span>
                      </div>

                      <div className={styles.cartActions}>
                        <div className={styles.quantity}>
                          <Button
                            variant="secondary"
                            aria-label={`Уменьшить количество: ${product.title}`}
                            onClick={() => setCart((current) => {
                              const entry = current[product.id];
                              if (!entry || entry.quantity <= 1) {
                                const next = { ...current };
                                delete next[product.id];
                                return next;
                              }
                              return {
                                ...current,
                                [product.id]: { ...entry, quantity: entry.quantity - 1 },
                              };
                            })}
                          >−</Button>
                          <span>{quantity}</span>
                          <Button
                            variant="secondary"
                            aria-label={`Увеличить количество: ${product.title}`}
                            disabled={quantity >= 99}
                            onClick={() => setCart((current) => ({
                              ...current,
                              [product.id]: {
                                ...current[product.id],
                                quantity: Math.min(99, current[product.id].quantity + 1),
                              },
                            }))}
                          >+</Button>
                        </div>

                        <strong className={styles.lineTotal}>
                          {money(price * quantity)}{currency === "RUB" ? ` ₽` : ` ${currency}`}
                        </strong>

                        <Button
                          variant="ghost"
                          onClick={() => setCart((current) => {
                            const next = { ...current };
                            delete next[product.id];
                            return next;
                          })}
                        >Удалить</Button>
                      </div>
                    </li>
                  );
                })}
              </ul>

              <div className={styles.cartTotal}>
                <span>Предварительная сумма</span>
                <strong>
                  {new Intl.NumberFormat("ru-RU", { maximumFractionDigits: 2 }).format(
                    Object.values(cart).reduce(
                      (sum, entry) => sum + Number(entry.product.price) * entry.quantity, 0,
                    ),
                  )}
                  {Object.values(cart)[0]?.product.currency
                    ? ` ${Object.values(cart)[0].product.currency}`
                    : " ₽"}
                </strong>
              </div>
              <p className={styles.cartNote}>
                Итоговая стоимость будет проверена сервером при оформлении заказа.
              </p>
              <form className={styles.orderForm} onSubmit={submitOrder}>
                <h3>Оформление заказа</h3>

                <label className={styles.formField}>
                  Ваше имя
                  <input
                    name="customer_name"
                    autoComplete="name"
                    value={customerName}
                    onChange={(event) => setCustomerName(event.target.value)}
                    required
                    maxLength={120}
                    placeholder="Как к вам обращаться"
                  />
                </label>

                <label className={styles.formField}>
                  Контакт для связи
                  <input
                    name="customer_contact"
                    autoComplete="email"
                    value={customerContact}
                    onChange={(event) => setCustomerContact(event.target.value)}
                    required
                    maxLength={255}
                    placeholder="Телефон, Telegram или email"
                  />
                </label>

                {orderError && <p className={styles.orderError} role="alert">{orderError}</p>}

                <Button type="submit" disabled={submitting}>
                  {submitting ? "Оформляем заказ…" : "Подтвердить заказ"}
                </Button>

                <p className={styles.cartNote}>
                  Оплаты на сайте нет. После оформления заказ будет сохранён в системе.
                </p>
              </form>

            </>
          )}
          {orderSuccess && <p className={styles.orderSuccess} role="status">{orderSuccess}</p>}
        </section>

        <footer className={styles.footer}>
            <span>тестовый магазин</span>
            <span><a href="https://t.me/kwadik" target="_blank">Kwadik</a></span>
          </footer>
        </Container>
      </main>
  );
}