import requests as rq

import bs4

HREF = 'https://store.steampowered.com/specials#p=0&tab=TopSellers'


def take_plays(n=8):
    n = min(50, n)

    response = rq.get(HREF)

    if response.status_code != 200:
        print(f'Error\nstatus_code >> {response.status_code}')
        return response.status_code

    code = response.content
    soup = bs4.BeautifulSoup(code, features='html.parser')

    output = []
    for i, item in enumerate(soup.find('div', id='TopSellersRows').find_all('a', class_='tab_item')):
        if i == n:
            break

        name = item.find('div', class_='tab_item_name').get_text(strip=True)
        old_price = item.find('div', 'discount_original_price').get_text(strip=True)
        new_price = item.find('div', 'discount_final_price').get_text(strip=True)

        output.append(f'{name} {old_price} >> {new_price}')

    return output + [f'Подробнее в официальном магазине: {HREF}']
