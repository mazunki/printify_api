#!/usr/bin/env python3

from products import Product
from providers import Provider
import json, csv

product_ids = Product.get_all_product_ids()
fields = "ProductID", "ProductName", "ProviderName", "ShippingCost", "VariantCount", "Norway?", "HandlingTime"

def get_printify_data_for_csv():
    for id_ in product_ids:
        try:
            product = Product(id_)
        except Warning as w:
            print("Warning:", w)
            continue

        product.fetch_data()
        if product._providers:
            for (provider, shipper) in product.shipping.items():
                for profile in shipper:
                    available_norway = "NO" in profile
                    yield product.id, product.title, provider.title, profile.cost, len(profile.variants), available_norway, shipper.handling_time


with open("printify.csv", "w") as f:
    writer = csv.writer(f, delimiter=";")
    writer.writerow(fields)


for row in get_printify_data_for_csv():
    with open("printify.csv", "a") as f:
        writer = csv.writer(f, delimiter=";")
        writer.writerow(row)
    
