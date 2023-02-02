import logging
import redis
import json

from environs import Env
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from functools import partial

from logger import TelegramLogHandler

from question import get_question


logger = logging.getLogger('Logger')

QUESTION, ANSWER, GIVE_UP, SCORE = range(4)


def main():
    env = Env()
    env.read_env()
    TELEGRAM_TOKEN = env('TELEGRAM_TOKEN')
    TELEGRAM_TOKEN_LOGS = env('TELEGRAM_TOKEN_LOGS')
    TG_CHAT_ID = env('TG_CHAT_ID')
    REDIS_HOST = env('REDIS_HOST')
    REDIS_PASS = env('REDIS_PASS')
    redis_conn = redis.StrictRedis(
            host=REDIS_HOST,
            port=11386,
            db=0,
            password=REDIS_PASS
        )
    bot = Bot(token=TELEGRAM_TOKEN_LOGS)

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogHandler(bot, TG_CHAT_ID))

    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    
    conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION:[
                MessageHandler(Filters.regex('Новый вопрос'), partial(question, redis_conn=redis_conn)),
                ],
            ANSWER:[
                MessageHandler(Filters.regex('Сдаться'), partial(give_up, redis_conn=redis_conn)),
                MessageHandler(Filters.text & ~Filters.command, partial(answer, redis_conn=redis_conn)),
                ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    dispatcher.add_handler(conversation)
    updater.start_polling()
    updater.idle()


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], 
                   ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте', reply_markup=reply_markup)
    return QUESTION
    

def question(update: Update, context: CallbackContext, redis_conn):
    question_to_send = get_question()
    redis_conn.set(update.effective_chat.id, json.dumps(question_to_send))
    context.bot.send_message(chat_id=update.effective_chat.id, text=question_to_send['Вопрос'])
    return ANSWER


def answer(update: Update, context: CallbackContext, redis_conn):
    answer = json.loads(redis_conn.get(update.effective_chat.id))['Ответ']
    if update.message.text == answer:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»')
        return QUESTION
    else:
        context.bot.send_message(
            chat_id=update.effective_chat.id,
            text=f'Неправильно :( Попробуешь еще раз? (Правильный ответ: {answer})')
        return ANSWER


def give_up(update: Update, context: CallbackContext, redis_conn):
    answer = json.loads(redis_conn.get(update.effective_chat.id))['Ответ']
    context.bot.send_message(chat_id=update.effective_chat.id, text=f'Правильный ответ: {answer}')
    question(update, context, redis_conn)


if __name__ == "__main__":
    main()