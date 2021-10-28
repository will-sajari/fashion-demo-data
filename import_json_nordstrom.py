import json
import random
import uuid
from datetime import tzinfo, timedelta, datetime, timezone
import sys

input_file = sys.argv[1]
output_file = sys.argv[2]

with open(f"./{input_file}") as jsonFile:
    jsonObject = json.load(jsonFile)
    jsonFile.close()

newList = []
uniqueSkus = []


def genRandSold():
    return random.randint(0, 1000)


def genRandMargin():
    return random.randint(5, 50)


def genRandSale():
    return str(bool(random.getrandbits(1))).lower()


def genWarehouseLocation():
    locations = ["Sydney", "Melbourne", "Brisbane"]
    return random.choice(locations)


def genUuid():
    return str(uuid.uuid4())


def genRatings():
    return random.randint(1, 5)


def genRatingCount():
    return random.randint(1, 300)


def genDateAdded():
    start_date = datetime(2021, 1, 1)
    end_date = datetime(2021, 10, 31)

    time_between_dates = end_date - start_date
    days_between_dates = time_between_dates.days
    random_number_of_days = random.randrange(days_between_dates)
    random_date = start_date + timedelta(days=random_number_of_days)
    timestamp = random_date.replace(tzinfo=timezone.utc).timestamp()

    return int(timestamp)


def genStock():
    return random.randint(0, 150)


categories = jsonObject["catalog"][0]["categories"]
categories_copy = jsonObject["catalog"][0]["categories"]
products = jsonObject["catalog"][1]["products"]

# map parent ids and names by looping through first dict of categories against the copy of the dict of categories
for category in categories:
    parent_id = category.get("parent_id")
    for category_copy in categories_copy:
        if parent_id == category_copy["id"]:
            category["parent_name"] = category_copy["name"]

for product in products:
    # check if the sku already exists
    if product["sku"] in uniqueSkus:
        continue
    else:
        # if not add the sku to the uniqueSkus list
        uniqueSkus.append(product["sku"])
        category_hierarchy = []
        for category in categories:
            if product["category_id"] == category["id"]:
                parent_category_name = category["parent_name"]
                category_name = category["name"]
                product["category_L1"] = parent_category_name
                product["category_L2"] = f"{parent_category_name} > {category_name}"
                category_hierarchy.append(parent_category_name)
                category_hierarchy.append(category_name)

        if "features" in product:
            for feature in product["features"]:
                values = list(feature.values())
                valueName = values[0].lower().replace(' ', '_')
                value = values[1].lower()
                product[valueName] = value
                product.pop("features")

        if "images" in product:
            imagesList = [image["url"] for image in product["images"]]
            product["images_list"] = imagesList
            product.pop("images")

        if "combinations" in product:
            variantIds = []
            quantityList = []
            priceList = []
            colorList = []
            sizeList = []
            widthList = []
            for variant in product["combinations"]:
                variantIds.append(variant["sku"])
                quantityList.append(variant["quantity"])
                priceList.append(variant["price"])
                if "features" in variant:
                    for feature in variant["features"]:
                        if feature["name"] == "color":
                            colorList.append(feature["value"])
                        if feature["name"] == "size":
                            sizeList.append(feature["value"])
                        if feature["name"] == "width":
                            widthList.append(feature["value"])
                if "images" in variant:
                    variantImages = [v["url"] for v in variant["images"]]
            product.pop("combinations")

            product["variant_ids"] = variantIds
            product["variant_quantity"] = quantityList
            product["variant_price"] = priceList
            product["variant_color"] = colorList
            product["variant_size"] = sizeList
            product["variant_width"] = widthList
            product["variant_images"] = variantImages

        product.pop("reviews_number")
        product.pop("description")
        product.pop("meta_description")
        product.pop("meta_keywords")
        product.pop("meta_title")
        product.pop("short_description")
        product.pop("quantity")
        product["category_hierarchy"] = category_hierarchy
        product["margin"] = genRandMargin()
        product["qty_sold"] = genRandSold()
        product["sale"] = genRandSale()
        product["warehouse_location"] = genWarehouseLocation()
        # product["uuid"] = genUuid() probably don't need uuid as we are only using unique skus
        product["rating"] = genRatings()
        product["rating_count"] = genRatingCount()
        product["date_added"] = genDateAdded()
        product["stock"] = genStock()

        newList.append(product)


with open(f'./data/{output_file}', 'w') as jsonFile:
    json.dump(newList, jsonFile)
    jsonFile.close()
