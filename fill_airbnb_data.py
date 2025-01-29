import pymongo
from bson.objectid import ObjectId
from datetime import datetime

client = pymongo.MongoClient("mongodb://localhost:27017/")
db = client["airbnb_prices"]  # Connect to the database
listingCollection = db["airbnb_data"]  # Connect to the airbnb_data collection
locationCollection = db["locations"]  # Connect to the locations collection
logsCollection = db["logs"]  # Create or connect to the collection

# Pagination settings
page_size = 10  # Number of listings per page
page_number = 1  # Current page number (1-based)

while True:
    try: 
        # Find all listings in airbnb_data where location is an empty string, with pagination
        missing_location_listings = listingCollection.find({
            "$or": [
                { "location": { "$exists": False } },
                { "location": "" },
                { "type": { "$exists": False } },
                { "type": "" },
                { "ownerName": { "$exists": False } },
                { "ownerName": "" }
            ]
        }).skip((page_number - 1) * page_size).limit(page_size)

        # Prepare a list to hold the updates
        updates = []
        listings_found = False
        
        for listing in missing_location_listings:
            listings_found = True  # At least one listing was found
            airbnbId = listing.get("airbnbId")
            
            # Find the corresponding location in the locations collection
            location_data = locationCollection.find_one({"airbnbId": airbnbId})
                    
            if location_data:
                listing["location"] = location_data.get("location")
                listing["ownerName"] = location_data.get("ownerName")
                listing["type"] = location_data.get("type")
                
                # If a location is found, prepare the update
                updates.append(
                    pymongo.UpdateOne(
                        {"_id": listing["_id"]},
                        {"$set": listing}    
                    )
                )

        # Perform the bulk update if there are updates to apply
        if updates:
            result = listingCollection.bulk_write(updates)
            print(f"Updated {result.modified_count} listings with location data on page {page_number}.")

        # Break the loop if no more listings are found
        if not listings_found:
            break

        page_number += 1
        
    except Exception as e:
        log = {
            "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            "data": "page:" + str(page_number),
            "when": "Failed to fill airbnb data",
            "message": str(e)
        }
        logsCollection.insert_one(log)            
        break

print(f"")
print(f"")
print(f"---------------------------------------------------------------")
print(f"FINISHED PROCESS: Preencher dados das localizações.")

client.close()
