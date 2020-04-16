import logging

import azure.functions as func
from selenium import webdriver

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request. 11:38')

    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')

    driver = webdriver.Chrome("/usr/local/bin/chromedriver", chrome_options=chrome_options)
    driver.get('http://www.ubuntu.com/')
    links = driver.find_elements_by_tag_name("a")
    link_list = ""
    for link in links:
        if link_list == "":
            link_list = link.text
        else:
            link_list = link_list + ", " + link.text

    return func.HttpResponse(
             str(link_list),
             status_code=200
    )