
import time
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By

from objects.location import Location
from objects.log import Log
from utils.chromedriver import get_chrome_driver
from utils.mongodb import Database_Config, get_database
from utils.print import print_green, print_red


def extract_listing_data(driver: WebDriver, obj: Location):

    # Find all listings
    type_element = driver.find_element(
        By.CSS_SELECTOR, 'h2[elementtiming="LCP-target"]')
    type = "Espaço inteiro" if "Espaço inteiro" in type_element.text else "Quarto"

    owner_name_element = driver.find_element(
        By.CSS_SELECTOR, 'div[data-section-id="HOST_OVERVIEW_DEFAULT"]')
    owner_name_split = owner_name_element.text.split('\n')
    name = owner_name_split[0].replace("Anfitriã(o): ", "")

    obj.type = type
    obj.typeCompleteDescription = type_element.text
    obj.ownerName = name

    return obj


driver = get_chrome_driver()

db, client = get_database()
locationCollection = db[Database_Config.LOCATION]
logsCollection = db[Database_Config.LOGS]

page_size = 10
page_number = 1

while True:
    try:
        missing_type_listings = locationCollection.find({
            "$or": [
                {"type": {"$exists": False}},
                {"type": ""}
            ]
        }).skip((page_number - 1) * page_size).limit(page_size)

        updates = []
        listings_found = False

        locations = [Location.from_dict(doc) for doc in missing_type_listings]

        for location in locations:
            listings_found = True
            try:
                print_green(
                    f"Obtendo mais informações do AIRBNB ({location.airbnbId})...")

                if "http" not in location.url:
                    location.url = "https://" + location.url

                driver.get(location.url)

                time.sleep(5)

                location = extract_listing_data(driver, location)

                update_result = locationCollection.update_one(
                    {"airbnbId": location.airbnbId},
                    {"$set": location.to_vars()}
                )

            except Exception as e:
                log = Log(
                    location.to_vars(), f"[ERRO] - Ocorreu ao obter informações para o AIRBNB ({location.airbnbId}), pode estar indisponível no momento", str(e))
                print_red(log.fixed_message)
                logsCollection.insert_one(log.to_vars())

        if not listings_found:
            break

        page_number += 1
    except Exception as e:
        log = Log("page: " + str(page_number),
                  f"[ERRO CRITICO] - Ocorreu ao obter mais informações do AIRBNB", str(e))
        print_red(log.fixed_message)
        logsCollection.insert_one(log.to_vars())
        break

print_green(f"")
print_green(f"")
print_green(f"---------------------------------------------------------------")
print_green(f"-> PROCESSO FINALIZADO: Obter o tipo da locação e salvar no Mongo.")

client.close()
driver.quit()
