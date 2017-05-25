from config import *
from bsmsgparser import *
import telebot
import logging
import statdb

logger = logging.getLogger('BSstatbot')

class BotHandler(logging.Handler):
    def __init__(self, bot):
        logging.Handler.__init__(self)
        self.bot_obj = bot
    def emit(self, record):
        msg = self.format(record)
        bot.send_message(OWNER_ID, msg, parse_mode='Markdown')


bot = telebot.TeleBot(TOKEN)
me = bot.get_me()

#@bot.message_handler(commands=['leave'])
#def leave_group(msg):
#    bot.leave_chat(msg.chat.id)


@bot.message_handler(commands=['id'], func=lambda msg: msg.from_user.id == OWNER_ID)
def say_id(msg):
    bot.reply_to(msg,msg.chat.id)


@bot.message_handler(commands=['связать'], func=lambda msg: msg.from_user.id == OWNER_ID)
def link_user(msg):
    pass


@bot.message_handler(commands=['кто'])
def who_user(msg):
    pass


@bot.message_handler(commands=['стат'])
def stat_user(msg):
    pass


@bot.message_handler(func=lambda msg: msg.chat.id == SUPPORT_CHAT_ID, content_types=['new_chat_member'])
def on_user_joins(msg):
    new_user = msg.new_chat_member
    if statdb.new_tlgr_user(new_user.id, new_user.username, new_user.first_name, new_user.last_name):
        logger.info('New user added(join)')
        bot.send_message(msg.chat.id, GREETING_TEXT % new_user.first_name, disable_web_page_preview=True, parse_mode='Markdown')


@bot.message_handler()
def on_bs_fwd(msg):
    new_user = msg.from_user
    if statdb.new_tlgr_user(new_user.id, new_user.username, new_user.first_name, new_user.last_name):
        logger.info('New user added(msg)')
    if msg.forward_from and msg.forward_from.id == BS_BOT_ID:
        logger.info('Got forward in') #%s', msg.chat)
        result = bs_fwd_parser(msg)
        if result: bot.send_message(msg.chat.id, result,  parse_mode='Markdown')


def logger_init():
    #Console logging
    console_formatter = logging.Formatter(
        '%(asctime)s (%(filename)s:%(lineno)d %(funcName)s) %(levelname)s - %(name)s: "%(message)s"'
    )
    console_output_handler = logging.StreamHandler()
    console_output_handler.setFormatter(console_formatter)
    console_output_handler.setLevel(logging.DEBUG)
    logger.addHandler(console_output_handler)

    #Logging via telegram
    bot_formatter = logging.Formatter('%(message)s')
    bot_output_handler = BotHandler(bot)
    bot_output_handler.setFormatter(bot_formatter)
    bot_output_handler.setLevel(logging.INFO)
    logger.addHandler(bot_output_handler)

    logger.setLevel(logging.DEBUG)
    #telebot.logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    logger_init()
    logger.info("BS Battle Stats bot running")
    bot.polling(True)
