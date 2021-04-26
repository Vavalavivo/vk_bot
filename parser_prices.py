import requests as rq

import bs4

from pprint import pprint

SITES = {
    'steam': 'https://store.steampowered.com/search/?term=#',
    'gog': 'https://www.gog.com/games/ajax/filtered?limit=20&search=#',
    'epic': 'https://www.epicgames.com/store/ru/browse?pageSize=30&q=#&sortBy=relevance&sortDir=DESC'
}

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141'
                  ' Safari/537.36 OPR/73.0.3856.438 (Edition Yx GX 03)'
}


def parser_steam(href, name):
    response = rq.get(href.replace('#', name))

    if response.status_code != 200:
        return [('Ошибка запроса к серверу', response.status_code)]

    code = response.content
    soup = bs4.BeautifulSoup(code, 'html.parser').find('div', id='search_results'). \
        find_all('a', class_='search_result_row ds_collapse_flag')

    if not soup:
        return [('Ничего не найдено по запросу', name)]

    output = []
    for i in range(min(3, len(soup))):
        nm = soup[i].find('div', class_='col search_name ellipsis'). \
            find('span', class_='title').get_text(strip=True)
        pr = soup[i].find('div', class_='search_price')
        if pr.select_one('span:nth-of-type(1)') is None:
            pass
        else:
            pr.select_one('span:nth-of-type(1)').decompose()
        output.append((nm, pr.get_text(strip=True)))
    output.append(('Подробнее', 'https://store.steampowered.com'))

    return output


def parser_gog(href, name):
    response = rq.get(href.replace('#', name)).json()

    items = response['products']

    if not items:
        return [('Ничего не найдено по запросу', name)]

    output = []
    for i in range(min(3, len(items))):
        nm = items[i]['title']
        pr = items[i]['price']['finalAmount'] + 'руб'
        output.append((nm, pr))
    output.append(('Подробнее', 'https://www.gog.com'))

    return output


def parser_epic(href, name):
    response = rq.get(href.replace('#', name), headers=HEADERS)

    if response.status_code != 200:
        return [('Ошибка запроса к серверу', response.status_code)]

    code = response.content
    soup = bs4.BeautifulSoup(code, 'html.parser')

    if not soup:
        return [('Ничего не найдено по запросу', name)]

    output = []
    for item in soup:
        nm = item.find('span', class_='css-2ucwu').get_text(strip=True)
        pr = item.find('span', class_='css-f5udm3-BodyText__bodyText').get_text(strip=True)
        output.append((nm, pr))
    output.append(('Подробнее', 'https://www.epicgames.com/store/ru/'))

    return output


def search(name):
    output = [
        parser_steam(SITES['steam'], name),
        parser_gog(SITES['gog'], name)
    ]

    return output
