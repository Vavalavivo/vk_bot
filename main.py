import vk_api

from parser_weather import take_info
from parser_news import take_news
from parser_plays import take_plays
from parser_prices import search
from lang import RU, EN

import time

import datetime as dt

import random

from pprint import pprint

TOKEN = 'f4649667ccb4e9f5f83e85da8bd82cf5ad3' \
        '628d6148d215a30a5774f4e4b71fa76b698a69c1017ea669bf'


class Data:
    DEFAULT_TIME = dt.time(hour=8, minute=0)

    users_timing = {}
    callbacks = {}

    session = None

    now = None

    LANGS = {
        'ru': RU,
        'en': EN
    }
    lang = LANGS['en']

    KEYS = {}

    ERRORS = {
        808: 'Ошибка, неверный аргумент ({1}) для выбранной функции ({0})'
             'Справочник доступен по команде: >help'.format,
        101: 'Этот бот не понимает команды ({})'.format
    }

    def __init__(self, session):
        self.session = session

    def send_text_message(self, to_id, text):
        self.session.method('messages.send', {'user_id': to_id, 'message': text, 'random_id': random.randint(0, 10000)})

    def checked(self, user_id):
        self.session.method('messages.markAsRead', {'peer_id': user_id, 'mark_conversation_as_read': 1})

    def notify(self, *args):
        return self.complete_news()

    def complete_news(self):
        weather = take_info(self.now)
        news = '--' + '\n--'.join(take_news())
        plays = '--' + '\n--'.join(take_plays())
        mes = f'Погода сегодня днем: {weather["t"]}C, ветер {weather["w"]}м/с\n' \
              f'Погода сейчас: {weather["tn"]}C, ветер {weather["wn"]}м/с\n' + news \
              + f'\nИгры сегодня со скидкой:\n{plays}'

        return mes

    def set_time(self, user_id, arg, *args):
        try:
            val = tuple(map(int, arg.split(':')))
            if val[0] > 23 or val[1] > 59:
                raise Exception
        except Exception:
            return self.ERRORS[808]('>set_time', arg)

        self.users_timing[user_id] = dt.time(hour=val[0], minute=val[1])
        self.callbacks[user_id] = True
        return 'OK'

    def can_callback(self, user_id, arg, *args):
        val = {'on': True, 'off': False}.get(arg, 'Error')
        if val == 'Error':
            return self.ERRORS[808]('>callback', arg)

        self.callbacks[user_id] = val
        return 'OK'

    def user_data(self, user_id, *args):
        output = f'Справочник: {self.lang[">set_time"]} 8:30 - установка времени оповещения\n' \
                 f'{self.lang[">callback"]} on/off - включение/выключение оповещения\n' \
                 f'{self.lang[">weather"]} - показывает погоду\n' \
                 f'{self.lang[">get_info"]} - высылает "готовые" новости\n' \
                 f'{self.lang[">news"]} n - показывает новсти (0 < n < 15 кол-во новстей)\n' \
                 f'{self.lang[">plays"]} n - показывате скиндки на игры (0 < n < 18)\n' \
                 f'{self.lang[">check"]} play - показывает скидки на игру (play)\n' \
                 f'{self.lang[">lang"]} ru - меняет язык команд на русский (en на английский)\n' \
                 f'{self.lang[">help"]} - справочник\nУстановленное время {self.users_timing[user_id]},' \
                 f'оповещения {self.callbacks[user_id]}'
        return output

    def get_weather(self, *args):
        weather = take_info(self.now)
        mes = f'Погода сегодня днем: {weather["t"]}C, ветер {weather["w"]}м/с\n' \
              f'Погода сейчас: {weather["tn"]}C, ветер {weather["wn"]}м/с\n'
        return mes

    def get_news(self, _, n, com):
        try:
            n = int(n)
            if 0 > n > 15:
                raise Exception
        except Exception:
            return self.ERRORS[808](com, n)

        mes = '-' + '\n-'.join(take_news(n))
        return mes

    def get_plays(self, _, n, com):
        try:
            n = int(n)
            if 0 > n > 18:
                raise Exception
        except Exception:
            return self.ERRORS[808](com, n)

        mes = '-' + '\n-'.join(take_plays(n))
        return mes

    def check_prices(self, _, name, *args):
        prices = search(name)

        sites = {
            0: 'Steam',
            1: 'Gog Store',
            2: 'Epic Games'
        }

        output = []
        for i, res in enumerate(prices):
            store = sites[i]
            interim = '--' + '\n--'.join(['{}>> {}'.format(*np) for np in res])
            output.append(f'{store}:\n' + interim)

        return '\n'.join(output)

    def change_lang(self, _, key, com):
        try:
            self.lang = self.LANGS[key]
        except Exception:
            return self.ERRORS[808](com, key)

        self.set_lang()
        return 'OK'

    def set_lang(self):
        self.KEYS = {
            self.lang['>help']: self.user_data,
            self.lang['>callback']: self.can_callback,
            self.lang['>set_time']: self.set_time,
            self.lang['>get_info']: self.notify,
            self.lang['>weather']: self.get_weather,
            self.lang['>news']: self.get_news,
            self.lang['>plays']: self.get_plays,
            self.lang['>check']: self.check_prices,
            self.lang['>lang']: self.change_lang
        }

    def nothing(self, user_id, _, com):
        self.checked(user_id)
        return self.ERRORS[101](com)


class Handler(Data):
    def __init__(self, *args):
        super().__init__(*args)
        self.set_lang()

    def identification(self, user_id, com, arg):
        fun = self.KEYS.get(com, self.nothing)
        self.send_text_message(user_id, fun(user_id, arg, com))


def main():
    vk = vk_api.VkApi(token=TOKEN)
    vk._auth_token()

    handler = Handler(vk)

    while True:
        time.sleep(0.4)

        try:
            response = vk.method('messages.getConversations', {'offset': 0, 'count': 20, 'filter': 'unread'})
        except Exception:
            continue
        handler.now = dt.datetime.fromtimestamp(vk.method('utils.getServerTime'))

        if handler.now.second == 0:

            for user, _ in filter(lambda g: g[1].hour == handler.now.hour and g[1].minute == handler.now.minute,
                                  handler.users_timing.items()):
                if not handler.callbacks[user]:
                    continue

                handler.send_text_message(user, handler.notify())

                continue

        if response['count'] == 0:
            continue

        from_id = response['items'][0]['last_message']['from_id']
        text = response['items'][0]['last_message']['text'].lower()

        if from_id not in handler.users_timing:
            handler.users_timing[from_id] = handler.DEFAULT_TIME
            handler.callbacks[from_id] = True

        try:
            com, arg = text.split(maxsplit=1)
        except Exception:
            com, arg = text, ''

        handler.identification(from_id, com, arg)


if __name__ == '__main__':
    main()
