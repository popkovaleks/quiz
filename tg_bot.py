import logging

from environs import Env
from telegram import Update, Bot
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters
from functools import partial

from logger import TelegramLogHandler


logger = logging.getLogger('Logger')


def main():
    env = Env()
    env.read_env()
    TELEGRAM_TOKEN = env('TELEGRAM_TOKEN')
    # PROJECT_ID = env('PROJECT_ID')
    TELEGRAM_TOKEN_LOGS = env('TELEGRAM_TOKEN_LOGS')
    TG_CHAT_ID = env('TG_CHAT_ID')


    bot = Bot(token=TELEGRAM_TOKEN_LOGS)

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogHandler(bot, TG_CHAT_ID))

    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher

    # send_response_with_project_id = partial(send_response, PROJECT_ID=PROJECT_ID)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()


def start(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте')


def echo(update: Update, context: CallbackContext):
    context.bot.send_message(chat_id=update.effective_chat.id, text=update.message.text)


if __name__ == "__main__":
    main()