import os
import telebot
import requests
import json
from datetime import datetime

# Токены из переменных окружения
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
NOTION_TOKEN = os.environ.get('NOTION_TOKEN')
NOTION_DATABASE_ID = os.environ.get('NOTION_DATABASE_ID')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, 
        "✅ Бот работает!\n\n"
        "Команды:\n"
        "/заказ [имя] - создать заказ\n"
        "/помощь - все команды")

@bot.message_handler(commands=['заказ'])
def create_order(message):
    try:
        parts = message.text.split()
        if len(parts) < 2:
            bot.reply_to(message, "Напиши: /заказ Петя")
            return
        
        client_name = parts[1]
        today = datetime.now().strftime("%y%m%d")
        order_code = f"{client_name.upper()}-{today}-1"
        
        # Создаем в Notion
        url = "https://api.notion.com/v1/pages"
        headers = {
            "Authorization": f"Bearer {NOTION_TOKEN}",
            "Content-Type": "application/json",
            "Notion-Version": "2022-06-28"
        }
        
        data = {
            "parent": {"database_id": NOTION_DATABASE_ID},
            "properties": {
                "Код заказа": {"title": [{"text": {"content": order_code}}]},
                "��лиент": {"select": {"name": client_name}},
                "Статус": {"select": {"name": "🔍 Поиск — жду цену"}},
                "Дата": {"date": {"start": datetime.now().isoformat()}}
            }
        }
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            bot.reply_to(message, 
                f"✅ Заказ создан: {order_code}\n"
                f"Клиент: {client_name}\n"
                f"Статус: 🔍 Поиск — жду цену")
        else:
            bot.reply_to(message, f"❌ Ошибка Notion: {response.status_code}")
            
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка: {str(e)}")

print("Bot started...")
bot.polling(none_stop=True)