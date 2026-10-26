from io import BytesIO

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import (
    BufferedInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)
from PIL import Image, UnidentifiedImageError
from sqlalchemy.exc import SQLAlchemyError

from app.core.config import settings
from app.core.database import SessionFactory
from app.services.products import (
    ProductCategoryNotFoundError,
    create_product,
)

MAX_IMAGE_SIZE = 10 * 1024 * 1024

dispatcher = Dispatcher()


def get_admin_ids() -> set[int]:
    result = set()
    for value in settings.telegram_admin_ids.split(","):
        value = value.strip()
        if value.isdigit():
            result.add(int(value))
    return result


def catalog_keyboard() -> InlineKeyboardMarkup | None:
    url = settings.telegram_webapp_url.strip()
    if not url.startswith("https://"):
        return None

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Открыть каталог",
                    web_app=WebAppInfo(url=url),
                )
            ]
        ]
    )


@dispatcher.message(CommandStart())
async def start_handler(message: Message) -> None:
    keyboard = catalog_keyboard()
    text = "У меня есть товар"

    if keyboard is None:
        text += "\nКаталог пока не настроен."

    await message.answer(text, reply_markup=keyboard)


@dispatcher.message(F.photo)
async def photo_handler(message: Message, bot: Bot) -> None:
    user_id = message.from_user.id if message.from_user else None

    if user_id not in get_admin_ids():
        await message.answer("Добавлять товары может только администратор.")
        return

    title = (message.caption or "").strip()
    if not title:
        await message.answer(
            "Добавь название товара в подпись к фотографии и отправь ещё раз."
        )
        return

    if len(title) > 255:
        await message.answer("Название должно быть не длиннее 255 символов.")
        return

    photo = message.photo[-1]
    if photo.file_size is not None and photo.file_size > MAX_IMAGE_SIZE:
        await message.answer("Изображение должно быть не больше 10 МБ.")
        return

    try:
        telegram_file = await bot.get_file(photo.file_id)
        if not telegram_file.file_path:
            await message.answer("Не удалось получить изображение.")
            return

        buffer = BytesIO()
        await bot.download_file(
            telegram_file.file_path,
            destination=buffer,
        )
        image_data = buffer.getvalue()

        if not image_data or len(image_data) > MAX_IMAGE_SIZE:
            await message.answer("Изображение пустое или превышает 10 МБ.")
            return

        with Image.open(BytesIO(image_data)) as image:
            image_format = image.format
            image.verify()

        content_types = {
            "JPEG": "image/jpeg",
            "PNG": "image/png",
            "WEBP": "image/webp",
        }
        content_type = content_types.get(image_format)

        if content_type is None:
            await message.answer("Поддерживаются JPEG, PNG и WebP.")
            return

        async with SessionFactory() as session:
            product = await create_product(
                session,
                title=title,
                description=None,
                image_data=image_data,
                content_type=content_type,
            )

    except (UnidentifiedImageError, OSError, ValueError):
        await message.answer("Не удалось обработать изображение.")
        return
    except ProductCategoryNotFoundError:
        await message.answer(
            "Не найдена категория по умолчанию. Проверь настройки каталога."
        )
        return
    except SQLAlchemyError:
        await message.answer("Не удалось сохранить товар в базе данных.")
        return
    except Exception:
        await message.answer("Не удалось добавить товар. Попробуй позже.")
        raise

    await message.answer(
        f"Товар «{product.title}» добавлен в каталог."
    )


@dispatcher.message()
async def default_handler(message: Message) -> None:
    keyboard = catalog_keyboard()
    text = "У меня есть товар"

    if keyboard is None:
        text += "\nКаталог пока не настроен."

    await message.answer(text, reply_markup=keyboard)