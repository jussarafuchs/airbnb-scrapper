
import csv
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from ansi_codes import enable_ansi_escape_codes
from objects.location import Location
from objects.log import Log
from utils.chromedriver import get_chrome_driver
from utils.mongodb import Database_Config, get_database
from utils.print import print_green, print_red

enable_ansi_escape_codes()

db, client = get_database()
data_collection = db[Database_Config.AIRBNB_DATA]

page_size = 10
page_number = 1

with open("airbnb_data.csv", mode="w", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    header_written = False
    
    while True:
        data_list = data_collection.find().skip(
            (page_number - 1) * page_size).limit(page_size)
        
        for data in data_list:
            if "_id" in data:
                del data["_id"]
            
            if not header_written:
                writer.writerow(data.keys())
                header_written = True
            
            writer.writerow(data.values())

        if data_list.retrieved == 0:
            break

        print_green(f"Buscando dados, pagina atual: {page_number}")
        page_number += 1
    
print_green(f"")
print_green(f"")
print_green(f"---------------------------------------------------------------")
print_green(f"Os dados foram exportados para o arquivo airbnb_data.csv.")
print_green(f"---------------------------------------------------------------")
print_green(f"")
print_green(f"")

client.close()
