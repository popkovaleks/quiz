import logging
import redis
import json
import random
import os

from environs import Env
from telegram import Update, Bot, ReplyKeyboardMarkup
from telegram.ext import Updater, CallbackContext, CommandHandler, MessageHandler, Filters, ConversationHandler
from functools import partial

from logger import TelegramLogHandler

from question import get_question, parse_questions


logger = logging.getLogger('Logger')

QUESTION, ANSWER, GIVE_UP, SCORE = range(4)


def start(update: Update, context: CallbackContext):
    custom_keyboard = [['Новый вопрос', 'Сдаться'], 
                   ['Мой счет']]
    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    context.bot.send_message(chat_id=update.effective_chat.id, text='Здравствуйте', reply_markup=reply_markup)
    return QUESTION
    

def send_question(update: Update, context: CallbackContext, redis_conn, questions):
    question_to_send = get_question(questions)
    redis_conn.set(update.effective_chat.id, json.dumps(question_to_send))
    context.bot.send_message(chat_id=update.effective_chat.id, text=question_to_send['Вопрос'])
    return ANSWER


def check_answer(update: Update, context: CallbackContext, redis_conn):
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
    send_question(update, context, redis_conn)


def main():
    env = Env()
    env.read_env()
    telegram_token = env('TELEGRAM_TOKEN')
    telegram_token_logs = env('TELEGRAM_TOKEN_LOGS')
    tg_chat_id = env('TG_CHAT_ID')
    redis_host = env('REDIS_HOST')
    redis_pass = env('REDIS_PASS')
    redis_port = env('REDIS_PORT')
    questions_dir = env('QUESTIONS_DIR')
    questions_file = env.str('QUESTIONS_FILE', default=random.choice(os.listdir(questions_dir)))
    redis_conn = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=0,
            password=redis_pass
        )
    bot = Bot(token=telegram_token_logs)

    logger.setLevel(logging.INFO)
    logger.addHandler(TelegramLogHandler(bot, tg_chat_id))

    questions = parse_questions(questions_file)

    updater = Updater(telegram_token)
    dispatcher = updater.dispatcher
    
    conversation = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            QUESTION:[
                MessageHandler(Filters.regex('Новый вопрос'), partial(send_question, redis_conn=redis_conn, questions=questions)),
                ],
            ANSWER:[
                MessageHandler(Filters.regex('Сдаться'), partial(give_up, redis_conn=redis_conn)),
                MessageHandler(Filters.text & ~Filters.command, partial(check_answer, redis_conn=redis_conn)),
                ]
        },
        fallbacks=[CommandHandler('start', start)]
    )
    
    dispatcher.add_handler(conversation)
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()