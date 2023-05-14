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
    fmt = "{:>10} {:<60} {:<30} {:>12} {:>15}"
    if product._providers:
        if product.is_available_in("NO"):
            print(product)
            print(fmt.format("Product ID", "Product name", "Provider", "Cost", "Variant #"))
            for provider, shipper in product.providers_in("NO"):
                for profile in shipper:
                    print(fmt.format(product.id, product.title, provider.title, str(profile.cost), len(profile.variants)))


