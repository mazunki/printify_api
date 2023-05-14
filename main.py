#!/usr/bin/env python3

from products import Product
from providers import Provider
import json

product_ids = Product.get_all_product_ids()

for id_ in product_ids:
    try:
        product = Product(id_)
    except Warning as w:
        print("Warning:", w)
        continue
    
    product.fetch_data()
    if product._providers:
        for provider, shipping in product.shipping.items():
            for profile in shipping.profiles_in_country("NO"):
                print(product)
                print("\t", provider, profile.get("first_item"), profile.get("countries"))
        

