import requests as rq

import bs4

HEADERS = {
    'user-agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141'
                  ' Safari/537.36 OPR/73.0.3856.434 (Edition Yx GX 03)',
    'accept': '*/*'
}

HREF = 'https://www.gismeteo.ru/weather-tolyatti-4429/'


def take_info(time):
    response = rq.get(HREF, headers=HEADERS)

    if response.status_code != 200:
        print(f'Error\nstatus_code >> {response.status_code}')
        return

    code = response.content
    soup = bs4.BeautifulSoup(code, features='html.parser')

    output = {}

    output['t'] = soup.find_all('div', class_='tabtempline tabtemp_0line clearfix')[0] \
        .find_all('div', class_='value')[-1] \
        .find_next('span', class_='unit unit_temperature_c').get_text(strip=True)

    output['w'] = soup.find('div', class_='widget__row widget__row_table widget__row_wind') \
        .find('div', class_='widget__item', attrs={'data-item': '5'}) \
        .find_next('span', class_='unit unit_wind_m_s').get_text(strip=True)

    output['tn'] = soup.find('div', class_='js_meas_container temperature tab-weather__value') \
        .find('span', class_='js_value tab-weather__value_l').get_text(strip=True)

    output['wn'] = soup.find('div', class_='widget__row widget__row_table widget__row_wind-or-gust') \
        .find_all('div', class_='widget__item')[time.hour // 3] \
        .find_next('span', class_='unit unit_wind_m_s').get_text(strip=True)

    return output
