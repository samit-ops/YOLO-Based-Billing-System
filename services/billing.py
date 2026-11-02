import json
import os

from services.inventory import (
    load_products,
    decrease_stock,
    increase_stock
)

DATABASE_PATH = os.path.join("data", "database.json")


def load_bill():
    with open(DATABASE_PATH, "r") as file:
        data = json.load(file)

    return data.get("bill", [])


def save_bill(bill):
    with open(DATABASE_PATH, "w") as file:
        json.dump({"bill": bill}, file, indent=2)


def add_item(product_class):
    products = load_products()

    if product_class not in products:
        return False, "Product is not in the catalog."

    product = products[product_class]
    bill = load_bill()

    success, message = decrease_stock(product_class)

    if not success:
        return False, message

    existing_item = None

    for item in bill:
        if item["class"] == product_class:
            existing_item = item
            break

    if existing_item:
        existing_item["quantity"] += 1
    else:
        bill.append({
            "class": product_class,
            "name": product["display_name"],
            "price": product["price"],
            "gst": product["gst"],
            "discount": product["discount"],
            "quantity": 1
        })

    save_bill(bill)

    return True, f"{product['display_name']} added to the bill."


def remove_item(product_class):
    bill = load_bill()
    item_found = None

    for item in bill:
        if item["class"] == product_class:
            item_found = item
            break

    if not item_found:
        return False, "Product is not in the bill."

    if item_found["quantity"] > 1:
        item_found["quantity"] -= 1
    else:
        bill.remove(item_found)

    increase_stock(product_class, 1)
    save_bill(bill)

    return True, "Product removed from the bill."


def calculate_bill():
    bill = load_bill()

    subtotal = 0
    total_discount = 0
    total_gst = 0
    items = []

    for item in bill:
        item_subtotal = item["price"] * item["quantity"]
        discount_amount = item_subtotal * item["discount"] / 100
        taxable_amount = item_subtotal - discount_amount
        gst_amount = taxable_amount * item["gst"] / 100
        final_amount = taxable_amount + gst_amount

        subtotal += item_subtotal
        total_discount += discount_amount
        total_gst += gst_amount

        items.append({
            **item,
            "item_subtotal": round(item_subtotal, 2),
            "discount_amount": round(discount_amount, 2),
            "gst_amount": round(gst_amount, 2),
            "final_amount": round(final_amount, 2)
        })

    total = subtotal - total_discount + total_gst

    return {
        "items": items,
        "subtotal": round(subtotal, 2),
        "total_discount": round(total_discount, 2),
        "total_gst": round(total_gst, 2),
        "total": round(total, 2)
    }


def clear_bill():
    bill = load_bill()

    for item in bill:
        increase_stock(item["class"], item["quantity"])

    save_bill([])

    return True
