import os, time
import threading
from threading import Thread
from flask import Flask, request, Response

from table import *

from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages import VideoMessage
from viberbot.api.messages.text_message import TextMessage

from viberbot.api.viber_requests import ViberConversationStartedRequest
from viberbot.api.viber_requests import ViberFailedRequest
from viberbot.api.viber_requests import ViberMessageRequest
from viberbot.api.viber_requests import ViberSubscribedRequest
from viberbot.api.viber_requests import ViberUnsubscribedRequest

# if os.name != 'posix': # для heroku
#     from dotenv import load_dotenv
#     load_dotenv()

VIBER_API_KEY = ''


app = Flask(__name__)
viber = Api(BotConfiguration(
    name='SmartViberBot',
    avatar='',
    auth_token=VIBER_API_KEY
))
last_request = read_data()

@app.route('/', methods=['GET'])
def inc():
    return "It's OK"

@app.route('/', methods=['POST'])
def incoming():

    print('---Обработка входящего сообщения.---')

    def answer(viber_message, sender_id):
        incoming_text = viber_message.text.lower().strip(' ?.')
        if len(incoming_text.split()) != 1:
            answer_text = 'Человек, ты используешь слишком много слов. Достаточно одного!'
        elif incoming_text == 'help' or incoming_text == 'хелп':
            answer_text = ('Этот бот разработан для автоматической смены '
                           'ответственного за обработку заявок ЦТО и ОСО. '
                           'Просто напишите в сообщении Имя, Фамилию или id ответственного. '
                           'Список сотрудников берется непосредственно из Bitrix24. '
                           'Для обновления списка сотрудников воспользуйтесь командой "Кто?"')
        elif incoming_text == 'кто':
            # зоздаем поток для запроса в Bitrix24
            thread_bx24 = Thread(
                target=set_tech_employee_list, args=(sender_id,))
            thread_bx24.start()
            answer_text = 'Запрос в Bitrix24 отправлен, подождите.'
        else:
            print('Ищем сотрудника. Значение tech_employee_list[0]: ',tech_employee_list[0])
            found_employee_list = employee_found_list(
                tech_employee_list, incoming_text)
            if not found_employee_list:
                answer_text = 'Таких человеков не найдено...'
            elif len(found_employee_list) == 1:
                responsible = found_employee_list[0]
                # thread_selenium = Thread(target=waiting, name=THREAD_NAME, args=(sender_id,))
                thread_selenium = Thread(target=change_responsible,
                                         name=THREAD_NAME, args=(TEMPLATE_LIST, responsible, sender_id,))
                if THREAD_NAME in (i.name for i in threading.enumerate()):
                    answer_text = 'Имей терпение, человек! Я уже меняю ответственного. Просто подожди!'
                else:
                    print('Запускаем Selenium')
                    thread_selenium.start()
                    # сделать запуск в виде отдельного потока
                    # status_selenium = change_responsible(TEMPLATE_LIST, responsible)
 
                    answer_text = 'Назначаю ответственного. Подождите...'
            elif len(found_employee_list) > 1:
                # список сотрудников для отправки
                answer_text = ('Надо выбрать всего одного человека, не двух, не трёх, а всего лишь '
                               'одного. Это же так просто, человек!\n' + '\n'.join(
                                   (i['ID'] + ' ' + i['NAME'] + ' ' + i['LAST_NAME']
                                    for i in found_employee_list)))
            else:
                answer_text = 'Произошло что-то странное...'
        return answer_text

    if not viber.verify_signature(request.get_data(), request.headers.get('X-Viber-Content-Signature')):
        return Response(status=403)

    viber_request = viber.parse_request(request.get_data())






    return Response(status=200)

        # if isinstance(viber_request, ViberMessageRequest):
        #     sender_id = viber_request.sender.id
        #     text = answer(viber_request.message, sender_id)
        #     message = TextMessage(text=text)
        #     viber.send_messages(sender_id, [message])
        # elif isinstance(viber_request, ViberFailedRequest):
        #     print('Ошибка...')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True, use_reloader=False)
