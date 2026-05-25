print("Привет! Бот работает!")

import requests
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

print("Токен найден?" , "ДА" if TOKEN else "НЕТ")

def search_wildberries(query):
    url = "https://search.wb.ru/exactmatch/ru/common/v18/search"
    params = {"query": query, "curr": "rub", "page": 1, "limit": 10}
    
    response = requests.get(url, params=params)
    if response.status_code != 200:
        return None
    
    data = response.json()
    products = []
    
    for product in data.get('data', {}).get('products', []):
        price = product['sizes'][0]['price']['basic'] // 100
        products.append({
            'name': product['name'],
            'price': price,
            'brand': product.get('brand', 'Нет бренда'),
            'id': product['id'],
            'rating': product.get('rating', 0)
        })
    return products

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🛍️ Привет! Я бот для поиска товаров на Wildberries!\n\n"
        "Просто напиши название товара, и я найду его.\n\n"
        "/help — помощь"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🔍 Напиши название товара, и я найду до 10 позиций на Wildberries.\n\n"
        "Примеры: наушники, футболка, смарт-часы"
    )

async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.message.text
    wait_msg = await update.message.reply_text(f"🔍 Ищу «{query}»...")
    
    products = search_wildberries(query)
    
    if not products:
        await wait_msg.edit_text(f"❌ Товары по запросу «{query}» не найдены.")
        return
    
    result = f"✅ Найдено {len(products)} товаров:\n\n"
    for i, p in enumerate(products, 1):
        price_str = f"{p['price']:,}".replace(',', ' ')
        result += f"{i}. *{p['brand']}*\n   {p['name'][:60]}\n   💰 {price_str} ₽\n   ⭐ {p['rating']}\n   [Ссылка](https://www.wildberries.ru/catalog/{p['id']}/detail.aspx)\n\n"
    
    await wait_msg.delete()
    await update.message.reply_text(result[:4000], parse_mode="Markdown", disable_web_page_preview=True)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
    