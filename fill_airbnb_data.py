from ansi_codes import enable_ansi_escape_codes
from objects.airbnb_data import Airbnb_Data
from objects.location import Location
from objects.log import Log
from utils.mongodb import Database_Config, get_database
from utils.print import print_green, print_red

enable_ansi_escape_codes()
db, client = get_database()
airbnb_data_collection = db[Database_Config.AIRBNB_DATA]
location_collection = db[Database_Config.LOCATION]
logs_collection = db[Database_Config.LOGS]

# Pagination settings
page_size = 10  # Number of listings per page
page_number = 1  # Current page number (1-based)

while True:
    try:
        # Find all listings in airbnb_data where location is an empty string, with pagination
        missing_location_listings = airbnb_data_collection.find({
            "$or": [
                {"location": {"$exists": False}},
                {"location": ""},
                {"type": {"$exists": False}},
                {"type": ""},
                {"ownerName": {"$exists": False}},
                {"ownerName": ""}
            ]
        }).skip((page_number - 1) * page_size).limit(page_size)

        listings_found = False

        airbnb_data_list = [Airbnb_Data.from_dict(doc)
                            for doc in missing_location_listings]

        for airbnb_data in airbnb_data_list:
            listings_found = True  # At least one listing was found
            try:
                airbnbId = airbnb_data.airbnbId

                # Find the corresponding location in the locations collection
                location_data = location_collection.find_one(
                    {"airbnbId": airbnbId})

                if location_data:
                    location = Location.from_dict(location_data)

                    airbnb_data.location = location.location
                    airbnb_data.ownerName = location.ownerName
                    airbnb_data.type = location.type

                    airbnb_data_collection.update_one(
                        {"_id": airbnb_data._id},
                        {"$set": airbnb_data.to_vars()}
                    )
                    print_green(f"Atualizado a localização do AIRBNB ({
                                airbnb_data.airbnbId})...")
            except Exception as e:
                log = Log(
                    airbnb_data.to_vars(), f"[ERRO] - Ocorreu ao salvar os dados da localização no AIRBNB ({airbnb_data.airbnbId}).", str(e))
                print_red(log.fixed_message)
                logs_collection.insert_one(log.to_vars())

        if not listings_found:
            break

        page_number += 1

    except Exception as e:
        log = Log("page:" + str(page_number),
                  f"[ERRO CRITICO] - Ocorreu ao salvar os dados de localização nos airbnb.", str(e))
        print_red(log.fixed_message)
        logs_collection.insert_one(log.to_vars())
        break

print_green(f"")
print_green(f"")
print_green(f"---------------------------------------------------------------")
print_green(
    f"-> PROCESSO FINALIZADO: Salvar dados de localização no airbnb_data.")

client.close()
