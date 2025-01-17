import numpy as np

from utils.parsing.general import get


def find_pagination(soup):
    # Проверяем наличие пагинации
    try:
        res = soup.find('div', class_='item-list').find('ul', class_='pager').find_all('li')
    except AttributeError:
        return None
    pagination_lst = np.array([i.text for i in res if i.text.isdigit()])[:-1]
    pagination_lst = np.insert(pagination_lst, 0, 0)
    return pagination_lst


def search_series(soup):
    # Ищем все серии по запросу
    try:
        res = soup.find('div', id='main').find('h3').find_next().find_all('li')
    except AttributeError:
        return None
    series_dict = {}
    for li in res:
        link = li.find('a').get('href')
        series = li.text
        series_dict[link] = series
    count_series = len(series_dict.keys())
    return series_dict, count_series


async def series_books(link):
    # Ищем все книги в выбранной серии
    url = f'http://flibusta.is{link}?page={0}'
    soup = await get(url)
    pagination_lst = find_pagination(soup)
    series_dict = {}
    if pagination_lst is not None:
        # Если есть пагинация - добавляем все книги со всех страниц
        for page in pagination_lst:
            url = f'http://flibusta.is{link}?page={page}'
            soup = await get(url)
            res = soup.find('div', id='main').find_all('form', action='/mass/download')
            for items in res:
                for item in items.find_all('a'):
                    href = item.get('href')
                    if href.startswith('/b/') and not href.endswith(('download', 'read', 'mail')):
                        series_dict[href] = item.text
    else:
        res = soup.find('div', id='main').find_all('form', action='/mass/download')
        for items in res:
            for item in items.find_all('a'):
                link = item.get('href')
                if link.startswith('/b/') and not link.endswith(('download', 'read', 'mail')):
                    series_dict[link] = item.text
    # series_dict = {link: series_name}
    return series_dict


def description_series(soup):
    # Ищем название серии, авторов, жанры
    res = soup.find('div', id='main').find_all('tbody')[1].find_all('tr')
    name = soup.find('h1', class_='title').text
    authors = res[1].text
    genres = res[-1].text

    return name, authors, genres
