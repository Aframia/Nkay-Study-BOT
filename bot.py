import telebot
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import schedule
import time
from threading import Thread

# Set up your bot token and Google Sheets credentials
BOT_TOKEN = '7889297579:AAHfBiILjeioKAP_-2Ga5GXJbiMmEDQi3Ng'
GROUP_CHAT_ID = '-1001706560104 '# Use this ID to send messages to your group
SHEET_ID = '1ZZOFeDbwqV7ac1z7PT3jq3c8nFyKDOmTl3HswDuc56Q'
PATH = '/Users/mac/Desktop/Nkay study bot/nkay-study-444611-8fe58f154f14.json'

# Initialize the bot
bot = telebot.TeleBot(BOT_TOKEN)

# Google Sheets setup
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name(PATH, scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(SHEET_ID).sheet1  # Open the first sheet

def send_daily_image():
    # Fetch image URL and callback data from Google Sheets
    image_url = sheet.cell(2, 1).value  # Assuming the image URL is in cell A2
    truth_message = sheet.cell(2, 2).value[:64] # Assuming Truth message is in cell B2
    lie_message = sheet.cell(2, 3).value[:64]  # Assuming Lie message is in cell C2

    # Send the image with buttons to the group chat
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(telebot.types.InlineKeyboardButton("Truth", callback_data=truth_message))
    markup.add(telebot.types.InlineKeyboardButton("Lie", callback_data=lie_message))
    
    bot.send_photo(chat_id=GROUP_CHAT_ID, photo=image_url, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Fetching appropriate messages from Google Sheets based on button clicked
    if call.data:
        if call.data == sheet.cell(2, 2).value[:64]:  # Check if it matches the Truth message
            response_message = sheet.cell(3, 2).value  # Assuming response for Truth is in cell B3
        elif call.data == sheet.cell(2, 3).value[:64]:  # Check if it matches the Lie message
            response_message = sheet.cell(3, 3).value  # Assuming response for Lie is in cell C3
        else:
            response_message = "Unknown selection."

        bot.answer_callback_query(call.id, response_message, show_alert=True)

def run_schedule():
    schedule.every().day.at("20:55").do(send_daily_image)
    
    while True:
        schedule.run_pending()
        time.sleep(1)

# Start the scheduling in a separate thread
Thread(target=run_schedule).start()

# Start polling for messages (if needed)
bot.polling(none_stop=True)

