import random
import vk_api as vk
import json
import redis
import os

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from environs import Env

from question import get_question, parse_questions


def start(event, vk_api):
    keyboard = VkKeyboard(one_time=False)
    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.POSITIVE)
    keyboard.add_button('Сдаться', color=VkKeyboardColor.NEGATIVE)
    keyboard.add_line()
    keyboard.add_button('Счет', color=VkKeyboardColor.PRIMARY)
    vk_api.messages.send(
        user_id=event.user_id,
        keyboard=keyboard.get_keyboard(),
        random_id=random.randint(1,1000),
        message='Привет'
    )


def send_question(event, vk_api, redis_conn, questions):
    question_to_send = get_question(questions)
    redis_conn.set(event.user_id, json.dumps(question_to_send))
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=random.randint(1,1000),
        message=question_to_send['Вопрос']
    )

def give_up(event, vk_api, redis_conn):
    answer = json.loads(redis_conn.get(event.user_id))['Ответ']
    vk_api.messages.send(
        user_id=event.user_id,
        random_id=random.randint(1,1000),
        message=f'Правильный ответ: {answer}'
    )
    send_question(event, vk_api, redis_conn)


def check_answer(event, vk_api, redis_conn):
    answer = json.loads(redis_conn.get(event.user_id))['Ответ']
    if event.text == answer:
        vk_api.messages.send(
            user_id=event.user_id,
            message='Правильно! Поздравляю! Для следующего вопроса нажми «Новый вопрос»',
            random_id=random.randint(1,1000),
            )
    else:
        vk_api.messages.send(
            user_id=event.user_id,
            message=f'Неправильно :( Попробуешь еще раз? (Правильный ответ: {answer})',
            random_id=random.randint(1,1000),
            )
        
    
if __name__ == "__main__":
    env = Env()
    env.read_env()
    redis_host = env('REDIS_HOST')
    redis_pass = env('REDIS_PASS')
    redis_port = env('REDIS_PORT')
    vk_api_token = env('VK_API_TOKEN')
    questions_dir = env('QUESTIONS_DIR')
    questions_file = env.str('QUESTIONS_FILE', default=random.choice(os.listdir(questions_dir)))
    questions = parse_questions(questions_file)

    redis_conn = redis.StrictRedis(
            host=redis_host,
            port=redis_port,
            db=0,
            password=redis_pass
        )

    vk_session = vk.VkApi(token=vk_api_token)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text=='/start':
            start(event, vk_api)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text=='Новый вопрос':
            send_question(event, vk_api, redis_conn, questions)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text=='Сдаться':
            give_up(event, vk_api, redis_conn)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me:
            check_answer(event, vk_api, redis_conn)
        

