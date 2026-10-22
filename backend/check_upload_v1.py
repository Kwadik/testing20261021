from app.services.storage import upload_product_image


if __name__ == "__main__":
    # Минимальный тестовый текст не является изображением,
    # поэтому здесь только проверяем отказ для неподдерживаемого типа.
    try:
        upload_product_image(b"test", "text/plain")
    except ValueError as exc:
        print(f"Validation works: {exc}")