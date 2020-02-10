from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
__token__ = ""

users = {}
chats = {}

class UserInfo:
    def __init__(self, telegram_user):
        self.username = telegram_user.username
        self.user = telegram_user
        self.roles = {}

    def add_role(self, chat, role):
        self.roles[chat] = role

    def role_in_chat(self, chat, bot, update):
        if chat not in self.roles:
            bot.sendMessage(update.message.chat_id, text = "У вас нет роли в этом чате или мне неизвестен этот чат")
        else:
            bot.sendMessage(update.message.chat_id, text = "У вас в этом чате роль %s" % self.roles[chat])

class ChatInfo:
    def __init__(self, chat):
        self.chat = chat
        self.roles = {}

    def add_role(self, user, role):
        self.roles[user] = role

    def ping(self, bot, update, role):
        response = ""
        for i in self.roles:
            if self.roles[i] == role:
                response += "@" + i + " "
        if len(response) != 0:
            bot.sendMessage(update.message.chat_id, text = response)

def log_params(method_name, update):
    logger.debug("Method: %s\nFrom: %s\nchat_id: %d\nText: %s" %
                (method_name,
                 update.message.from_user,
                 update.message.chat_id,
                 update.message.text))

def myrole(bot, update):
    log_params('myrole', update)
    text = update.message.text
    chatname = update.message.chat_id
    telegram_user = update.message.from_user
    if telegram_user.id not in users:
        users[telegram_user.id] = UserInfo(telegram_user, update.message.username)
    if chatname not in chats:
        chats[chatname] = ChatInfo(chatname)
    user = users[telegram_user.id]
    user.role_in_chat(chatname, bot, update)

def ping(bot, update):
    log_params('ping', update)
    text = update.message.text
    role = ""
    can = 0
    for a in text:
        if a == ' ':
            can = can + was
            was = 0
        elif a != ' ':
            was = 1
            if can == 1:
                role += a
    chatname = update.message.chat_id
    if chatname not in chats:
        chats[chatname] = ChatInfo(chatname)
    chat = chats[update.message.chat_id]
    chat.ping(bot, update, role)
    
def promote(bot, update):
    log_params('promote', update)
    text = update.message.text
    username = ""
    role = ""
    can = 0
    was = 1
    for a in text:
        if a == ' ':
            can = can + was
            was = 0
        elif a != ' ':
            was = 1
            if can == 1:
                if a != '@':
                    username += a
            if can == 2: 
                role += a
    if len(username) == 0 or len(role) == 0:
        bot.sendMessage(update.message.chat_id, text="Usage: /promote username role")
        return
    chatname = update.message.chat_id
    telegram_user = update.message.from_user
    if telegram_user.id not in users:
        users[telegram_user.id] = UserInfo(telegram_user)
    user = users[telegram_user.id]
    user.add_role(chatname, role)
    if chatname not in chats:
        chats[chatname] = ChatInfo(chatname)
    chat = chats[chatname]
    chat.add_role(username, role)
    response = "Теперь " + username + " " + role;
    bot.sendMessage(update.message.chat_id, text=response)

def start(bot, update):
    log_params('start', update)
    telegram_user = update.message.from_user
    if telegram_user.id not in users:
        users[telegram_user.id] = UserInfo(telegram_user)
        bot.sendMessage(chat_id=update.message.chat_id, text="Добро пожаловать в клуб. Я - бот, дающий роли в телеграмме.")
        return
    bot.sendMessage(chat_id=update.message.chat_id, text="Я рад вас снова видеть, я - бот дающий роли в телеграмме")

def help(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id, text="Пока я умею только определять какая у вас роль(/myrole), давать человеку a роль x в чате(/promote a x), призывать в чате всех, у кого роль x, /ping x")

if __name__ == '__main__':
    updater = Updater(token=__token__)
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    role_handler = CommandHandler('myrole', myrole)
    promote_handler = CommandHandler('promote', promote)
    ping_handler = CommandHandler('ping', ping)
    updater.dispatcher.add_handler(promote_handler)
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(ping_handler)
    updater.dispatcher.add_handler(role_handler)
    updater.start_polling()
    updater.idle()
