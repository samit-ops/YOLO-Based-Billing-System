import json
import os

PRODUCTS_PATH = os.path.join("config", "products.json")


def load_products():
    with open(PRODUCTS_PATH, "r") as file:
        return json.load(file)


def save_products(products):
    with open(PRODUCTS_PATH, "w") as file:
        json.dump(products, file, indent=2)


def decrease_stock(product_class):
    products = load_products()

    if product_class not in products:
        return False, "Product is not in the catalog."

    if products[product_class]["stock"] <= 0:
        return False, "Product is out of stock."

    products[product_class]["stock"] -= 1
    save_products(products)

    return True, "Stock successfully reduced."


def increase_stock(product_class, quantity=1):
    products = load_products()

    if product_class not in products:
        return False, "Product is not in the catalog."

    products[product_class]["stock"] += quantity
    save_products(products)

    return True, "Stock successfully restored."


def get_inventory():
    products = load_products()

    inventory = []

    for product_class, product in products.items():
        stock = product["stock"]

        if stock == 0:
            status = "OUT OF STOCK"
        elif stock <= product["minimum_stock"]:
            status = "LOW STOCK"
        else:
            status = "AVAILABLE"

        inventory.append({
            "class": product_class,
            "name": product["display_name"],
            "price": product["price"],
            "stock": stock,
            "minimum_stock": product["minimum_stock"],
            "status": status
        })

    return inventory
