import asyncio
import html
import logging
import os
import re
import feedparser
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters import Command
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# --- CONFIG ---
API_TOKEN = "8705880761:AAF6w9OYwB0ZhfdcKggpXp21Bo9CmwMn6w0"
MY_ID = 133724864

bot = Bot(token=API_TOKEN)
dp = Dispatcher()
scheduler = AsyncIOScheduler()

SOURCES = {
    "Movies 🎬": "https://www.digitalspy.com/rss/all/movies.xml",
    "IT/Tech 💻": "https://www.theverge.com/rss/index.xml",
    "Education 📚": "http://feeds.bbci.co.uk/news/education/rss.xml",
    "Travel ✈️": "https://www.independent.co.uk/travel/rss",
    "Food 🍕": "https://www.delish.com/rss/all.xml",
    "Health & Sport 💪": "http://rss.cnn.com/rss/cnn_health.rss"
}

# --- TOOLS ---
def clean_html(raw_html):
    if not raw_html: return ""
    cleanr = re.compile('<.*?>|&nbsp;|\xa0')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return html.unescape(cleantext).strip()

def get_chunks(text):
    if not text: return "No description available."
    sentences = re.split(r'(?<=[.!?]) +', text)
    return " ".join(sentences[:2])

def get_vocabulary(text):
    clean_text = re.sub(r'http\S+', '', text)
    words = re.findall(r'\b[a-zA-Z]{9,}\b', clean_text)
    stop_words = ['everything', 'something', 'background', 'advertising', 'published', 'description']
    filtered = [w.lower() for w in words if w.lower() not in stop_words]
    return list(set(filtered))[:3]

# --- CORE LOGIC ---
async def send_daily_digest():
    print("Fetching real news for Masha...")
    digest_message = "<b>Morning Digest for your Blog!</b> ☕️\n\n"
    
    for category, url in SOURCES.items():
        try:
            feed = feedparser.parse(url)
            if feed.entries:
                entry = feed.entries[0]
                title = entry.title
                desc = clean_html(entry.get('summary', ''))
                short_desc = get_chunks(desc)
                vocab = get_vocabulary(desc + " " + title)
                
                digest_message += f"<b>{category}</b>\n"
                digest_message += f"📌 {title}\n"
                digest_message += f"📝 {short_desc}\n"
                if vocab:
                    digest_message += f"💡 <i>Vocab: {', '.join(vocab)}</i>\n"
                digest_message += f"🔗 <a href='{entry.link}'>Read more</a>\n\n"
        except Exception as e:
            print(f"Error in {category}: {e}")

    await bot.send_message(MY_ID, digest_message, parse_mode="HTML", disable_web_page_preview=True)

# --- HANDLERS ---
@dp.message(Command("start", "digest"))
async def manual_digest(message: types.Message):
    if message.from_user.id == MY_ID:
        await message.answer("Starting to collect news, wait a sec...")
        await send_daily_digest()

async def main():
    print("BOT STARTED WITH FULL LOGIC")
    # Schedule for 11:00 AM
    scheduler.add_job(send_daily_digest, 'cron', hour=11, minute=0)
    scheduler.start()
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
