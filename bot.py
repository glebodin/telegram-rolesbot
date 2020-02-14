from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import User, TelegramObject
import logging
logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
__token__ = "1029606728:AAFTBl55fwDkEf25zz9Z1KWY7thvuTiry_g"

users = {}
logins = {}
chats = {}

class UserInfo:
    def __init__(self, username):
        self.username = username
        self.roles = {}

    def add_role(self, chat, role):
        self.roles[chat] = role

    def role_in_chat(self, chat, bot, update):
        if chat not in self.roles:
            bot.sendMessage(update.message.chat_id, text = "У вас нет роли в этом чате или мне неизвестен этот чат")
        else:
            bot.sendMessage(update.message.chat_id, text = "У вас в этом чате роль %s" % self.roles[chat])
    
    def update(self, chat, userid):
        self.username = get_chat_member(chat, userid)

class ChatInfo:
    def __init__(self, chat):
        self.chat = chat
        self.roles = {}

    def add_role(self, user_id, role):
        self.roles[user_id] = role

    def ping(self, bot, update, role):
        response = ""
        for i in self.roles:
            if self.roles[i] == role:
                users[i].update(chat, i)
                response += "@" + users[i].username + " "
        if len(response) != 0:
            bot.sendMessage(update.message.chat_id, text = response)

def log_params(method_name, update):
    logger.debug("Method: %s\nFrom: %s\nchat_id: %d\nText: %s" %
                (method_name,
                 update.message.from_user,
                 update.message.chat_id,
                 update.message.text))

def get(bot, username):
    members = bot.get_chat_members
    for member in members:
        if username == member.user.username:
            return member.user.id
    return "No such member"

def newchat(bot, update):
    chatname = update.message.chat_id
    chats[chatname] = ChatInfo(chatname)
    admins = bot.get_chat_administrators(chatname)
    for admin in admins:
        username = admin.user.username
        userid = admin.user.id
        chats[chatname].add_role(userid, "admin")
        if userid not in users:
            users[userid] = UserInfo(username)
            logins[username] = userid
        users[userid].add_role(chatname, "admin")

def myrole(bot, update):
    log_params('myrole', update)
    chatname = update.message.chat_id
    if chatname not in chats:
        newchat(bot, update)
    text = update.message.text
    username = update.message.from_user.username
    userid = update.message.from_user.id
    if userid not in users:
        users[userid] = UserInfo(username)
        logins[username] = userid
    users[userid].role_in_chat(chatname, bot, update)

def ping(bot, update):
    log_params('ping', update)
    chatname = update.message.chat_id
    if chatname not in chats:
        newchat(bot, update)
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
    chat = chats[update.message.chat_id]
    chat.ping(bot, update, role)
    
def promote(bot, update):
    log_params('promote', update)
    chatname = update.message.chat_id
    if chatname not in chats:
        newchat(bot, update)
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
    if username not in logins:
         bot.sendMessage(update.message.chat_id, text="Я пока не знаю такого пользователя или он сменил имя, может ли он мне написать /start?") #так как текущее апи не позволяет по username определить user_id, то приходится сохранить их в отдельном месте и если мы не знаем такого username просить человека написать start
         return;
    userid = logins[username]
    if userid not in users:
        users[userid] = UserInfo(username)
        logins[username] = userid
    user = users[userid]
    user.add_role(chatname, role)
    chat = chats[chatname]
    chat.add_role(username, role)
    response = "Теперь " + username + " " + role;
    bot.sendMessage(update.message.chat_id, text=response)

def start(bot, update):
    log_params('start', update)
    chatname = update.message.chat_id
    if chatname not in chats:
        newchat(bot, update)
    username = update.message.from_user.username
    userid = update.message.from_user.id
    if userid not in users:
        users[userid] = UserInfo(username)
        logins[username] = userid
        bot.sendMessage(chat_id=update.message.chat_id, text="Добро пожаловать в клуб. Я - бот, дающий роли в телеграмме.")
        return
    bot.sendMessage(chat_id=update.message.chat_id, text="Я рад вас снова видеть, я - бот дающий роли в телеграмме")

def allroles(bot, update):
    log_params('allroles', update)
    chatname = update.message.chat_id
    if chatname not in chats:
        newchat(bot, update)
    chat = chats[chatname]
    response = ""
    for user in chat.roles:
        response += "У " + users[user].username + " Роли : " + chat.roles[user]
    bot.sendMessage(chat_id=update.message.chat_id, text=response)

def help(bot, update):
    chatname = update.message.chat_id
    if chatname not in chats:
        newchat(bot, update)
    bot.sendMessage(chat_id=update.message.chat_id, text="Пока я умею только определять какая у вас роль(/myrole), давать человеку a роль x в чате(/promote a x), призывать в чате всех, у кого роль x(/ping x), вывести все роли в текущем чате(/allroles)")

if __name__ == '__main__':
    updater = Updater(token=__token__)
    start_handler = CommandHandler('start', start)
    help_handler = CommandHandler('help', help)
    allroles_handler = CommandHandler('allroles', allroles)
    role_handler = CommandHandler('myrole', myrole)
    promote_handler = CommandHandler('promote', promote)
    ping_handler = CommandHandler('ping', ping)
    updater.dispatcher.add_handler(promote_handler)
    updater.dispatcher.add_handler(start_handler)
    updater.dispatcher.add_handler(allroles_handler)
    updater.dispatcher.add_handler(help_handler)
    updater.dispatcher.add_handler(ping_handler)
    updater.dispatcher.add_handler(role_handler)
    updater.start_polling()
    updater.idle()
