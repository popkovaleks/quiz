import random
import vk_api as vk
import json
import redis

from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor
from environs import Env

from question import get_question


def echo(event, vk_api):
    vk_api.messages.send(
    user_id=event.user_id,
    message=event.text,
    random_id=random.randint(1,1000)
        )


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


def question(event, vk_api, redis_conn):
    question_to_send = get_question()
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
    question(event, vk_api, redis_conn)


def answer(event, vk_api, redis_conn):
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
    REDIS_HOST = env('REDIS_HOST')
    REDIS_PASS = env('REDIS_PASS')
    VK_API_TOKEN = env('VK_API_TOKEN')

    redis_conn = redis.StrictRedis(
            host=REDIS_HOST,
            port=11386,
            db=0,
            password=REDIS_PASS
        )

    vk_session = vk.VkApi(token=VK_API_TOKEN)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)


    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text=='/start':
            start(event, vk_api)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text=='Новый вопрос':
            question(event, vk_api, redis_conn)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text=='Сдаться':
            give_up(event, vk_api, redis_conn)
        elif event.type == VkEventType.MESSAGE_NEW and event.to_me:
            answer(event, vk_api, redis_conn)
        

