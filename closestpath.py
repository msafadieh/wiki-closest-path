"""
Finds the shortest path between two wikipedia articles.

Please use sparingly.
"""
from queue import Queue
import re
from sys import argv
from bs4 import BeautifulSoup
import requests

URL_REGEX = (r"/wiki/(?!(?:Talk|Wikipedia|User|Template|Template_talk"
             r"|Category|Help|File|Special)\:)([^#\"]+)")


def closest_path(url_1, url_2):
    """
        Finds the closest path between two articles on Wikpedia.

        :param url_1: Starting article
        :param url_2: Endpoint article
        :returns Dictionary with url key and optionally a parent key
                 or an empty dictionary
    """
    starting_article = re.search(URL_REGEX, url_1)
    end_article = re.search(URL_REGEX, url_2)

    if not (starting_article and end_article):
        raise Exception("Incorrect url format.")

    goal = end_article.group(1)

    to_compare, to_lookup = Queue(), Queue()
    to_compare.put({"url": starting_article.group(1)})
    visited = set()

    while not to_compare.empty():

        article = to_compare.get()

        if article["url"] not in visited:

            if article["url"] == goal:

                return article

            to_lookup.put(article)
            visited.add(article["url"])

        if to_compare.empty():

            populate_queue(to_compare, to_lookup.get())

    return {}


def fetch_page(url):
    """
        Makes a GET request to a Wikipedia article and extracts raw body.

        :param url: Wikipedia article URL  (e.g. "/wiki/Python")
        :return raw HTML body of the article
    """
    print(f"Loading {url}")
    wiki_url = "https://en.wikipedia.org/wiki/" + url
    response = requests.get(wiki_url).text
    soup = BeautifulSoup(response, features="html5lib")
    urls = soup.find("div", {"id": "bodyContent"})
    return urls.decode()


def get_all_urls(page, article):
    """
        finds all the linked Wikipedia URLs on a certain page

        :param page: Raw wikipedia HTML body
        :param article: Dictionary with "url" pointing to a Wikipedia article
        :return Set of Wikipedia article URLs
    """
    matches = re.findall(URL_REGEX, page)

    unique_matches = set(matches)
    if article["url"] in unique_matches:
        unique_matches.remove(article["url"])
    return unique_matches


def populate_queue(queue, article):
    """
        fetches the article and puts all the links in it
        on the queue

        :param queue: Queue object to populate
        :article Dictionary with "url" pointing to a Wikipedia article
    """
    response = fetch_page(article["url"])
    for child_url in get_all_urls(response, article):
        queue.put({"url": child_url, "parent": article})


def generate_string(answer):
    """
        generates proper string representation of the article
        chain

        :param answer: dictionary with url key and optionally a parent key
        :return string representation
    """
    parent = answer.get("parent")

    if parent:
        return f"{generate_string(parent)} --> {answer['url']}"

    return answer["url"]


def main():
    """
        Main function. Get two Wikipedia articles and finds closest link.
    """
    try:
        answer = closest_path(argv[1], argv[2])
        if answer:
            print(generate_string(answer))
        else:
            print("No link found.")
    except IndexError:
        print("Usage: python closestpath.py [first_url] [second_url]")


if __name__ == "__main__":
    main()
