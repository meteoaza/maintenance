import bot_token
import telebot
import time
import mybot_messages as mes


bot = telebot.TeleBot(bot_token.token)


@bot.message_handler(commands=['status', 'value'])
def botStatus(m):
    text = m.text.split()
    command = text[0]
    try:
        sens = text[1]
    except IndexError:
        sens = 'None'
    if command == '/status':
        answer = f'status of {sens}'
    elif command == '/value':
        answer = f'value of {sens}'
    bot.send_message(m.chat.id, answer)

@bot.message_handler(content_types=['text'])
def sendError(m, err):
    bot.send_message(m.chat.id, err)

def readDB():
    while True:
        with open('bot_DB.txt', 'r')as f:
            db_file = f.read()
        print(db_file)
        if 'Azat' in db_file:
            sendError(db_file)
        # if error:
        #     botError()
        # return db_file
        time.sleep(10)


if __name__ == '__main__':
    readDB()
    bot.polling(none_stop=True)