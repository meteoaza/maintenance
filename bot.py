import bot_token
import telebot
import time
import ast
import bot_constant as const

known_users = []
user_step = {}
data = {}

try:
    with open('bot_users.txt', 'r')as f:
        known_users = [int(user) for user in f.read().split('\n')]
except FileNotFoundError:
    pass


def listener(messages):
    """
    When new messages arrive TeleBot will call this function.
    """
    for m in messages:
        if m.content_type == 'text':
            text_mes = str(m.chat.first_name) + " [" + str(m.chat.id) + "]: " + m.text
            # send the sent message to admin( me:) )
            bot.send_message(bot_token.myChatId, text_mes)
            try:
                with open('bot_listener.log', 'a')as f:
                    f.write(text_mes + '\n')
            except UnicodeEncodeError:
                pass


bot = telebot.TeleBot(bot_token.token)
bot.set_update_listener(listener)  # register listener


# t = threading.Thread(target=bot.polling, kwargs={'none_stop': True, 'interval': 5, 'timeout': 30})

@bot.message_handler(commands=['start'])
def command_start(m):
    cid = m.chat.id
    # print(known_users, cid)
    if cid not in known_users:  # if user hasn't used the "/start" command yet:
        known_users.append(cid)  # save user id, so you could brodcast messages to all users of this bot later
        text = ([str(user) for user in known_users])
        with  open('bot_users.txt', 'w')as f:
            f.write('\n'.join(text))
        user_step[cid] = 0  # save user id and his current "command level", so he can use the "/getImage" command
        bot.send_message(cid, "Приветствую тебя, прямоходящий....")
        time.sleep(2)
        bot.send_message(cid, f"Я метео бот, а ты походу {m.chat.first_name}")
        time.sleep(2)
        bot.send_message(cid, "Я тебя запомнил...")
        time.sleep(3)
        command_help(m)  # show the new user the help page
    else:
        bot.send_message(cid, f"{m.chat.first_name}, мы с тобой уже знакомы, нет смысла знакомиться повторно!")


@bot.message_handler(commands=['help'])
def command_help(m):
    commands = const.commands
    cid = m.chat.id
    help_text = "На данный момент доступны следующие команды: \n"
    for key in commands:  # generate help text out of the commands dictionary defined at the top
        help_text += "/" + key + ": "
        help_text += commands[key] + "\n"
    bot.send_message(cid, help_text)  # send the generated help page


@bot.message_handler(commands=['status'])
def botStatus(m):
    cid = m.chat.id
    data = readDB()
    try:
        status = data['status']
        text = m.text.split()
        sens = text[1].upper()
        if sens == 'ALL':
            for s, v in status.items():
                answer = f'{s} = {v}'
                bot.send_message(cid, answer)
        elif sens == 'SENSORS':
            l = []
            for s in status.keys():
                l.append(s)
            bot.send_message(cid, f"Список доступных датчиков {','.join(l)}")
        else:
            try:
                answer = status[sens]
                bot.send_message(cid, answer)
            except KeyError:
                bot.send_message(cid, "Введите правильное имя датчика ")
    except (KeyError, IndexError):
        bot.send_message(cid, "Проверьте введенную команду ")


@bot.message_handler(commands=['value'])
def botValue(m):
    cid = m.chat.id
    data = readDB()
    try:
        value = data['value']
        text = m.text.split()
        sens = text[1].upper()
        if sens == 'ALL':
            for s, v in value.items():
                answer = f'{s} = {v}'
                bot.send_message(cid, answer)
        elif sens == 'SENSORS':
            l = []
            for s in value.keys():
                l.append(s)
            bot.send_message(cid, f"Список доступных датчиков {','.join(l)}")
        else:
            try:
                answer = value[sens]
                bot.send_message(cid, answer)
            except KeyError:
                bot.send_message(cid, "Введите правильное имя датчика ")
    except (KeyError, IndexError):
        bot.send_message(cid, "Проверьте введенную команду ")


@bot.message_handler(func=lambda message: True,
                     content_types=['audio', 'video', 'document', 'text', 'location', 'contact', 'sticker'])
def botMessage(m):
    cid = m.chat.id
    if m.text.upper() == 'PING':
        bot.send_message(cid, "Я на месте и в полной боевой готовности!!!")
    elif m.text.upper() == 'USERS' and cid == bot_token.myChatId:
        bot.send_message(bot_token.myChatId, known_users)
    else:
        bot.send_message(cid, 'Что-то я тебя не пойму никак...')


def readDB():
    with open('bot_data.txt', 'r')as f:
        data = f.read()
        data = ast.literal_eval(data)
    return data


if __name__ == '__main__':
    bot.polling(none_stop=True, interval=5)
