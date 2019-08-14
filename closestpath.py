from queue import Queue
import re
from sys import argv
from bs4 import BeautifulSoup
import requests

URL_REGEX = r"/wiki/(?!(?:Template|Template_talk|Category|Help|File|Special)\:)([^#]+)"

def closest_path(url_1, url_2):

    match_1 = re.search(URL_REGEX, url_1)
    match_2 = re.search(URL_REGEX, url_2)
    
    if not (match_1 and match_2):
        raise Exception("Incorrect url format.")

    match_goal = match_2.group(1)

    queue, to_lookup = Queue(), Queue()
    queue.put({"url": match_1.group(1)})
    visited = set()

    while not queue.empty():
        url = queue.get()
        if url["url"] not in visited:
            if url["url"] == match_goal:
                return url
            to_lookup.put(url)
            visited.add(url["url"])
        if queue.empty():
            populate_queue(queue, to_lookup.get())

def fetch_page(url):
    print(f"Loading {url}")
    wiki_url = "https://en.wikipedia.org/wiki/" + url
    response = requests.get(wiki_url).text
    soup = BeautifulSoup(response, features="html5lib")
    urls = soup.find("div", {"id": "bodyContent"})
    return urls.decode()

def get_all_urls(page, url):
    matches = re.findall(r"href=\"\/wiki\/(?!(?:Template|Template_talk|Category|Help|File|Special)\:)([^#]+?)\"", page)
    
    unique_matches = set(matches)
    if url["url"] in unique_matches:
        unique_matches.remove(url["url"])
    return unique_matches

def populate_queue(queue, url):
    response = fetch_page(url["url"])
    for child_url in get_all_urls(response, url):
        queue.put({"url": child_url, "parent": url})

def generate_string(answer):
    parent = answer.get("parent")
    if parent:
        return f"{generate_string(parent)} --> {answer['url']}"
    else:
        return answer["url"]

def main():
    try:
        answer = closest_path(argv[1], argv[2])
        if answer:
            print(generate_string(answer))
        else:
            print("No link found.")
    except IndexError:
        "Usage: python closestpath.py [first_url] [second_url]"

if __name__ == "__main__":
    main()
