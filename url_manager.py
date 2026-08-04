def load_urls():
    with open("url_list.txt", "r") as file:
        urls = file.readlines()

    return [url.strip() for url in urls]