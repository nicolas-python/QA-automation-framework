def load_urls():
    with open("url_list.txt", "r") as file:
        urls = file.readlines()

    return [url.strip() for url in urls]

def save_url(url):
    with open("url_list.txt", "a") as file:
        file.write(url + "\n")

def delete_url(url):
    urls = load_urls()
    urls.remove(url)

    with open("url_list.txt", "w") as file:
        for item in urls:
            file.write(item + "\n")