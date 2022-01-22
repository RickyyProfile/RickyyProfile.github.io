import requests
from selenium import webdriver
from bs4 import BeautifulSoup
import json


cookies = None
try:
    with open(r'cookies.json', "r") as f:
        cookies = json.load(f)
except FileNotFoundError:
    driver = webdriver.Edge()
    driver.get("https://aimware.net/forum/user/login")

    input("Press Enter after logging in...")

    cookies = driver.get_cookies()
    driver.close()

    with open(r'cookies.json', 'w') as f:
        json.dump(cookies, f)


session = requests.Session()

for cookie in cookies:
    session.cookies.set(cookie['name'], cookie['value'])



def get_usergroup(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    usergroup = soup.select("section.col-lg-12.section-base.section-content > span")[0].text
    if usergroup == "Administrator":
        return "admin"
    elif usergroup == "Super Moderator":
        return "supermod"
    elif usergroup == "Beta Tester":
        return "beta"
    elif usergroup == "Reseller":
        return "reseller"
    elif usergroup == "VIP":
        return "vip"
    elif usergroup == "Registered":
        return "registered"
    elif usergroup == "Banned":
        return "banned"


def get_last_page(url):
    r = session.get(url)
    soup = BeautifulSoup(r.text, "html.parser")
    try:
        a = soup.select("li.page-item")[4].find("a").get("href")
        return int(a.split("/")[-1])
    except IndexError:
        return 1


threads = []
already_seen = []
script_sections = ["https://aimware.net/forum/board/97", "https://aimware.net/forum/board/96"]


for script_section in script_sections:
    page_count = get_last_page(script_section)
    print("Scraping " + script_section + "...")
    for i in range(1, page_count + 1):
        print("Page: " + str(i))
        r = session.get(script_section + "/page/" + str(i))
        soup = BeautifulSoup(r.text, "html.parser")
        rows = soup.select(".row .forum-thread-list")
        for row in rows:
            title = row.find("a")
            thread_link = "https://aimware.net" + title.get("href")
            thread_title = title.get_text().replace("\n", "")

            author = row.select(".forum-thread-author")[0]
            thread_author = author.get_text()
            thread_author_link = "https://aimware.net" + author.find("a").get("href")
            thread_author_group = get_usergroup(thread_author_link)

            thread_replies = row.select(".d-none")[1].get_text()
            thread_views = row.select(".d-none")[2].get_text()

            if thread_title + thread_author not in already_seen:
                threads.append({
                    "link": thread_link,
                    "title": thread_title.replace("[Release] ", "").replace("[release] ", ""),
                    "author": thread_author,
                    "author_link": thread_author_link,
                    "author_group": thread_author_group,
                    "replies": thread_replies.replace(",", ""),
                    "views": thread_views.replace(",", ""),
                    "thread_count": 1
                })
                already_seen.append(thread_title + thread_author)


thread_count = {}
for thread in threads:
    if thread["author"] not in thread_count:
        thread_count[thread["author"]] = 1
    else:
        thread_count[thread["author"]] += 1


for thread in threads:
    if thread["author"] in thread_count:
        thread["thread_count"] = thread_count[thread["author"]]


with open(r'threads.json', 'w') as f:
    json.dump(threads, f, indent=4)
