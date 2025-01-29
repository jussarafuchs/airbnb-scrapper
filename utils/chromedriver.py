
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from objects.log import Log
from utils.mongodb import Database_Config, get_database
from utils.print import print_red


def get_chrome_driver():
    db, client = get_database()
    logsCollection = db[Database_Config.LOGS]

    try:
        # Set up Chrome options
        chrome_options = Options()
        # Run in headless mode (no GUI)
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")

        # Path to your ChromeDriver
        service = Service('chromedriver.exe')

        # Create a new instance of the Chrome driver
        driver = webdriver.Chrome(service=service, options=chrome_options)
    except Exception as e:
        log = Log("Chrome driver precisa ser atualizado!",
                  "Chrome driver precisa ser atualizado!", str(e))
        print_red("---------------------------------------------")
        print_red("---------------------------------------------")
        print_red(log.fixed_message)
        print_red("---------------------------------------------")
        print_red("---------------------------------------------")
        logsCollection.insert_one(log.to_vars())

    client.close()

    return driver
