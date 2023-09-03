import pandas as pd
import requests
import xml.etree.ElementTree as ET

URL_EUROPE = "https://rss.nytimes.com/services/xml/rss/nyt/Europe.xml"
URL_US = "https://rss.nytimes.com/services/xml/rss/nyt/US.xml"
URL_WORLD = "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"

item_elements = {
    "title": "Title",
    "author": "Author",
    "pubDate": "Published",
    "link": "Link",
    "category": "Categories",
    "description": "Description",
}

channel_elements = {
    "title": "Feed",
    "link": "Link",
    "lastBuildDate": "Last Build Date",
    "pubDate": "Publish Date",
    "language": "Language",
    "category": "Categories",
    "managingEditor": "Editor",
    "description": "Description",
}


def scrape_news(url, limit):
    response = requests.get(url=url)
    tree = ET.fromstring(response.text)
    channel = tree.find('channel')

    result = {}
    for key, value in channel_elements.items():
        try:
            if key != "category":
                result[key] = channel.find(key).text.encode("ascii", "ignore").decode()
            else:
                all_categories = [category.text.encode("ascii", "ignore").decode() for category in
                                  channel.findall(key)]
                if all_categories:
                    result[key] = all_categories
        except AttributeError:
            continue

    items_list = []
    for item in channel.findall("item"):
        if len(items_list) == limit:
            break
        items_dict = {}
        for key, value in item_elements.items():
            try:
                if key != "category":
                    items_dict[key] = item.find(key).text.encode("ascii", "ignore").decode()
                else:
                    all_categories = [category.text.encode("ascii", "ignore").decode() for category in
                                      item.findall(key)]
                    if all_categories:
                        items_dict[key] = all_categories
            except AttributeError:
                continue
        items_list.append(items_dict)

    if items_list:
        result["items"] = items_list

    data_table_title = f"{'_'.join(result['title'].split()[2:])}_{'_'.join(result['pubDate'].split()[1:4])}"

    df = pd.DataFrame(items_list)
    df.to_csv(f"{data_table_title}.csv")


if __name__ == "__main__":
    scrape_news(URL_EUROPE, 20)
    scrape_news(URL_US, 20)
    scrape_news(URL_WORLD, 20)
