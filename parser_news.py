import requests as rq

import bs4

from random import randint

HREF = 'https://tlt.ru'


def get_random_items(sequence, n):
    output = []
    for i in range(n):
        index = randint(0, len(sequence) - 1)
        output.append(sequence[index])
        sequence.pop(index)

    return output


def get_top_items(sequence, n):
    sequence.sort(key=lambda teg: int(teg.find_all('span', class_='h-p-b-p')[1].get_text(strip=True)))
    return [sequence.pop() for _ in range(n)]


def take_news(n=7):
    n = min(25, n)

    response = rq.get(HREF)

    if response.status_code != 200:
        print(f'Error\nstatus_code >> {response.status_code}')
        return response.status_code

    code = response.content
    soup = bs4.BeautifulSoup(code, features='html.parser')

    output = []

    for item in get_top_items(soup.find_all('div', class_='post-list-item'), n):
        tittle = item.find('div', class_='page-text-row').find('a').get_text(strip=True)
        output.append(tittle)

    return output + [f'Подробнее на певроисточнике: {HREF}']
