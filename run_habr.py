import requests
import bs4
from fake_headers import Headers
import re

KEYWORDS = ['дизайн', 'фото', 'web', 'python']
HOST = "https://habr.com"
ARTICLES = f"{HOST}/ru/all/"


def get_headers():
    return Headers(browser="firefox", os="win").generate()


def get_text(url):
    return requests.get(url, headers=get_headers()).text


def parse_article(article_tag):
    link_tag = article_tag.find("a", class_="tm-title__link")
    preview_article = article_tag.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-1")
    if not preview_article:
        preview_article = article_tag.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-2")
    if link_tag is None:
        return
    return {
        "date": article_tag.find("time")["title"],
        "link": f'{HOST}{link_tag["href"]}',
        "title": link_tag.find("span").text,
        "preview_article": preview_article.text,
    }


def find_words_in_preview_articles_and_print(words, articles):
    for article in articles:
        parsed = parse_article(article)
        if any(word.lower() in parsed["preview_article"].lower() for word in words):
            print(f"{parsed['date']} - {parsed['title']} - {parsed['link']}")


def find_words_in_full_articles_and_print(words, articles):
    for article in articles:
        parsed = parse_article(article)
        html = get_text(parsed['link'])
        soup = bs4.BeautifulSoup(html, features="html5lib")
        full_article = soup.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-1")
        if not full_article:
            full_article = soup.find("div", class_="article-formatted-body article-formatted-body article-formatted-body_version-2")
        parsed['full_article'] = full_article.text
        if any(word.lower() in parsed["full_article"].lower() for word in words):
            print(f"{parsed['date']} - {parsed['title']} - {parsed['link']}")


if __name__ == "__main__":
    html = get_text(f"{ARTICLES}")
    soup = bs4.BeautifulSoup(html, features="html5lib")
    articles = soup.find(class_="tm-articles-list").find_all("article", id=re.compile(r"\d+"))

    find_words_in_preview_articles_and_print(KEYWORDS, articles)
    print("\n***********************************************************************************\n")
    find_words_in_full_articles_and_print(KEYWORDS, articles)
