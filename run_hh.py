import requests
import bs4
from fake_headers import Headers
import json

KEYWORDS = ["Django", "Flask"]
HOST = "https://spb.hh.ru"
VACANCIES = f"{HOST}/search/vacancy?text=python&area=1&area=2"


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def parse_vacancies(divs):
    vacancies = []
    for div in divs:
        href = div.find("a")['href']
        try:
            compensation = div.find("span", attrs={'data-qa': 'vacancy-serp__vacancy-compensation'}).text
        except:
            compensation = None
        employer = div.find("a", attrs={'data-qa': 'vacancy-serp__vacancy-employer'}).text
        city = div.find("div", attrs={'data-qa': 'vacancy-serp__vacancy-address'}).text
        vacancies.append({
            'href': href,
            'compensation': compensation,
            'employer': employer,
            'city': city,
        })
    return vacancies


def find_words_in_full_vacancies(words, vacancies):
    result = []
    for vacancie in vacancies:
        html = get_text(vacancie['href'])
        soup = bs4.BeautifulSoup(html, features="html5lib")
        full_vacancie = soup.find("div", attrs={'data-qa': 'vacancy-description'}).text
        if any(word.lower() in full_vacancie.lower() for word in words):
            result.append(vacancie)
    return result

def filter_vacansies_by_compensation(filter, vacancies):
    result = []
    for vacancie in vacancies:
        if vacancie['compensation'] and filter in vacancie['compensation']:
            result.append(vacancie)
    return result

if __name__ == "__main__":
    html = get_text(f"{VACANCIES}")
    soup = bs4.BeautifulSoup(html, features="html5lib")
    divs = soup.find_all("div", class_="serp-item")
    vacancies = parse_vacancies(divs)
    vacancies_dollars = filter_vacansies_by_compensation('$', vacancies)
    result = find_words_in_full_vacancies(KEYWORDS, vacancies_dollars)

    with open('result.json', 'w', encoding='utf-8') as f:
        f.write(json.dumps(result, ensure_ascii=False, indent=3))
