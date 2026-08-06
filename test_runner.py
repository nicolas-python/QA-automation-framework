import  requests                        #Requests zum Prüfen von Webseiten und APIs per HTTP-Anfragen,urls prüfen und Serverantworten auszulesen


def run_test(url):
    response = requests.get(url)

    print("URL:", url)
    print("Status:", response.status_code)