# pip install pymongo
# # pip install selenium

from selenium.webdriver.common.by import By
import time
import json
import re
from datetime import datetime
from bson.objectid import ObjectId

from objects.log import Log
from utils.chromedriver import get_chrome_driver
from utils.mongodb import Database_Config, get_database
from utils.print import print_green, print_red


def extract_price(listing_text):
    if listing_text:
        lines = listing_text.split('\n')

        price = 0
        originalPrice = 0
        totalPrice = 0

        for line in lines:
            if 'por noite' in line:
                priceSplit = line.split(',')
                price = int(getNumbers(priceSplit[0]))

                if ',' in line:
                    originalPrice = int(getNumbers(priceSplit[1]))

            if 'Total' in line:
                totalPrice = int(getNumbers(line))

        return price, originalPrice if originalPrice else price, totalPrice
    return 0, 0, 0


def getNumbers(priceText):
    return re.sub(r'[^0-9]', '', priceText) if priceText else ""


def extract_rating(listing_text):
    lines = listing_text.split('\n')
    ratingText = lines[-1]

    if ratingText == "Novo":
        return "", ""

    ratingSplit = ratingText.split(' ')

    rating = ratingSplit[0] if len(ratingSplit) > 0 else ""
    reviews = getNumbers(ratingSplit[1]) if len(ratingSplit) > 0 else ""

    return rating, reviews


def clearLineBreak(text):
    textSplit = text.split('\n')
    return textSplit[0]


def getAirbnbId(text):
    textSplit = text.split('?')
    urlSplit = textSplit[0].split('rooms/')
    return urlSplit[1]


def extract_listing_data(listing):

    title_element = listing.find_element(
        By.CSS_SELECTOR, 'div[data-testid="listing-card-title"]')
    title = title_element.text if title_element else "N/A"

    name_element = listing.find_element(
        By.CSS_SELECTOR, 'meta[itemprop="name"]')
    name = name_element.get_attribute('content') if name_element else "N/A"

    subname_element = listing.find_element(
        By.CSS_SELECTOR, 'div[data-testid="listing-card-subtitle"]:nth-child(3)')
    subname = clearLineBreak(
        subname_element.text) if subname_element else "N/A"

    url_element = listing.find_element(By.CSS_SELECTOR, 'meta[itemprop="url"]')
    url = url_element.get_attribute('content') if url_element else "N/A"

    airbnbId = getAirbnbId(url)

    price_element = listing.find_element(
        By.CSS_SELECTOR, 'div[data-testid="price-availability-row"]')
    priceText = price_element.text if price_element else ""

    rating, reviews = extract_rating(listing.text)

    price, originalPrice, totalPrice = extract_price(priceText)

    creationDate = datetime.now().strftime('%Y-%m-%d')

    # Prepare the document to insert into MongoDB
    listing_data = {
        "_id": ObjectId(),
        "airbnbId": airbnbId,
        "title": title,
        "name": name,
        "subname": subname,
        "price": price,
        "originalPrice": originalPrice,
        # "totalPrice": totalPrice,
        "url": url,
        "rating": rating,
        "reviews": reviews,
        "location": "",
        "ownerName": "",
        "type": "",
        "creationDate": creationDate
    }

    return listing_data


driver = get_chrome_driver()

db, client = get_database()
airbnb_data_collection = db[Database_Config.AIRBNB_DATA]
executions_collection = db[Database_Config.EXECUTIONS]
location_collection = db[Database_Config.LOCATION]
logs_collection = db[Database_Config.LOGS]

# Get the current date for the error log file name
current_date = datetime.now().strftime('%Y-%m-%d')

# Check if today's execution already exists
if executions_collection.find_one({"executionDate": current_date}):
    print_green("Today's execution already exists. Exiting.")
    client.close()
    driver.quit()
    exit()

with open('config.json', 'r') as file:
    config_file = json.load(file)

all_listings_data = []  # List to hold all listing data

for file_data in config_file['location']:
    url = file_data["url"]
    location_name = file_data["name"]

    while url:
        try:
            # Open the URL
            driver.get(url)

            # Wait for the page to load
            time.sleep(5)  # Adjust sleep time as necessary

            # Find all listings
            listings = driver.find_elements(By.CSS_SELECTOR, 'div[itemprop="itemListElement"]')

            listings_data = []  # List to hold listing data

            for listing in listings:
                try:
                    obj = extract_listing_data(listing)

                    location_data = location_collection.find_one({"airbnbId": obj["airbnbId"]})
                    if location_data:
                        obj["location"] = location_data.get("location")
                        obj["ownerName"] = location_data.get("ownerName")
                        obj["type"] = location_data.get("type")

                    obj["city"] = location_name

                    listings_data.append(obj)
                    all_listings_data.append(obj)
                except Exception as e:
                    log = Log(
                        listing, f"[ERRO] - Ocorreu ao carregar dados de um AIRBNB específico.", str(e))
                    print_red(log.fixed_message)
                    logs_collection.insert_one(log.to_vars())
                    continue

            if listings_data:
                airbnb_data_collection.insert_many(listings_data)

            print_green(f"Salvando informações de {str(len(listings_data))} AIRBNB...")
        except Exception as e:
            log = Log(
                listing, f"[ERRO] - Ocorreu ao carregar os dados do site AIRBNB.", str(e))
            print_red(log.fixed_message)
            logs_collection.insert_one(log.to_vars())
            continue

        try:
            urlElement = driver.find_element(By.CSS_SELECTOR, 'a[aria-label="Próximo"]')
            url = urlElement.get_attribute('href')
        except Exception as e:
            url = ""


try:
    for listing in all_listings_data:
        airbnb_id = listing['airbnbId']

        if not location_collection.find_one({"airbnbId": airbnb_id}):
            airbnb_id_object = {
                "airbnbId": airbnb_id,
                "url": listing['url'],
                "location": "",
                "ownerName": "",
                "type": "",
                "city": listing["city"]
            }
            location_collection.insert_one(airbnb_id_object)

    executions_collection.insert_one({
        "_id": ObjectId(),
        "executionDate": datetime.now().strftime('%Y-%m-%d'),
        "rowsInserted": len(all_listings_data)
    })

except Exception as e:
    log = Log(
        listing, f"[ERRO] - Ocorreu ao salvar os dados da localização dos novos AIRBNB de hoje.", str(e))
    print_red(log.fixed_message)
    logs_collection.insert_one(log.to_vars())

print_green(f"")
print_green(f"")
print_green(f"---------------------------------------------------------------")
print_green(f"-> PROCESSO FINALIZADO: Obter dados do airbnb e salvar no MongoDB.")

# Close the MongoDB connection and the browser
client.close()
driver.quit()
