from telegram import Bot
import asyncio

async def get_emoji_ids():
    bot = Bot(token="8636524725:AAHY7j6yHm5fo3H2uLFs9GzZbBQsPj5fLeY")
    sticker_set = await bot.get_sticker_set("FinanceEmoji")
    for sticker in sticker_set.stickers:
        print(f"{sticker.emoji} = {sticker.file_unique_id} | custom_emoji_id: {getattr(sticker, 'custom_emoji_id', 'нет')}")

asyncio.run(get_emoji_ids())
