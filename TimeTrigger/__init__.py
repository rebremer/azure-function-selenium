import datetime
import logging

import azure.functions as func
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.storage.blob import BlobServiceClient
from datetime import datetime, timezone
import os

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.now().replace(tzinfo=timezone.utc).isoformat()

    logging.info('Python timer trigger function ran at %s', utc_timestamp)

    # see https://stackoverflow.com/questions/76568489/python-selenium-chromedriver-error-webdriver-init-got-an-unexpected-keywo
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

    driver.get('http://www.ubuntu.com/')
    links = driver.find_elements(By.TAG_NAME, "a")
    link_list = ""
    for link in links:
        if link_list == "":
            link_list = link.text
        else:
            link_list = link_list + ", " + link.text
    
    # create blob service client and container client
    credential = DefaultAzureCredential()
    storage_account_url = "https://" + os.environ["par_storage_account_name"] + ".blob.core.windows.net"
    client = BlobServiceClient(account_url=storage_account_url, credential=credential)
    blob_name = "test" + str(datetime.now()) + ".txt"
    blob_client = client.get_blob_client(container=os.environ["par_storage_container_name"], blob=blob_name)
    blob_client.upload_blob(link_list)
