import asyncio
import random
import html
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ChatMemberStatus
from aiogram.filters import Command
from config import BOT_TOKEN, CALL_WORDS, CHUNK_SIZE, DELAY
from database import add_or_update_user, deactivate_user, get_active_users

# Эмодзи для упоминаний
EMOJIS = ["🔥", "⚡", "💥", "✨", "🌟"]

# ID твоей группы
CHAT_ID = -1001993637210

bot = Bot(BOT_TOKEN)
dp = Dispatcher()


# ===============================
# /id — показывает ID чата
# ===============================
@dp.message(Command("id"))
async def get_chat_id(msg: types.Message):
    await msg.reply(f"Chat ID: {msg.chat.id}")


# ===============================
# Загрузка участников (только админы)
# ===============================
async def load_initial_members(chat_id: int):
    print("Loading members...")
    try:
        admins = await bot.get_chat_administrators(chat_id)
        for admin in admins:
            add_or_update_user(admin.user)
    except Exception as e:
        print("Admin load error:", e)

    print("Telegram не выдаёт полный список участников. "
          "Пользователи будут появляться при активности.")
    print("Members loaded.")


# ===============================
# Кликабельное эмодзи-упоминание
# ===============================
def emoji_mention(uid: int) -> str:
    emoji = random.choice(EMOJIS)
    return f'<a href="tg://user?id={uid}">{emoji}</a>'


# ===============================
# Обработка сообщений
# ===============================
@dp.message()
async def handler_message(msg: types.Message):
    if msg.chat.type in ("group", "supergroup") and msg.from_user:
        add_or_update_user(msg.from_user)

    if not msg.text:
        return

    raw = msg.text.strip()
    low = raw.lower()

    # поддержка тем
    thread_id = msg.message_thread_id

    # Проверяем все кодовые слова
    if any(low.startswith(word) for word in CALL_WORDS):

        # текст после кодового слова
        parts = raw.split(" ", 1)
        user_text = html.escape(parts[1]) if len(parts) > 1 else ""

        users = get_active_users()
        await call_everyone(msg.chat.id, users, user_text, thread_id)


# ===============================
# Обработка входа/выхода
# ===============================
@dp.chat_member()
async def handler_member(event: types.ChatMemberUpdated):
    user = event.new_chat_member.user
    status = event.new_chat_member.status

    if status in (
        ChatMemberStatus.MEMBER,
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER
    ):
        add_or_update_user(user)

    elif status in (ChatMemberStatus.LEFT, ChatMemberStatus.KICKED):
        deactivate_user(user)


# ===============================
# Функция вызова
# ===============================
async def call_everyone(chat_id: int, users, user_text: str, thread_id: int | None):

    ids = [u.id for u in users]

    for i in range(0, len(ids), CHUNK_SIZE):
        chunk = ids[i:i + CHUNK_SIZE]

        # строка эмодзи-упоминаний
        mention_line = "".join(emoji_mention(uid) for uid in chunk)

        # если есть текст — добавляем
        if user_text:
            text = f"{mention_line}\n{user_text}"
        else:
            text = mention_line

        await bot.send_message(
            chat_id,
            text,
            parse_mode="HTML",
            message_thread_id=thread_id
        )

        await asyncio.sleep(DELAY)


# ===============================
# Запуск
# ===============================
async def main():
    await asyncio.sleep(1)
    await load_initial_members(CHAT_ID)
    print("PhoenixCall activated")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
