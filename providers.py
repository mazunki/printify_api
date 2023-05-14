#!/usr/bin/env python
from printify import Printify
import requests

class Location:
    def __init__(self, location):
        self.data = location
        self.address = location.get("address1", None), location.get("address2", None)
        self.city = location.get("city")
        self.country = location.get("country", None)
        self.region = location.get("region", None)
        self.zip = location.get("zip", None)

    def is_in(self, country):
        return self.country in ("REST_OF_THE_WORLD", country)

    def __str__(self):
        return self.country

class Provider(Printify):
    BASE_URL = f"{Printify.PRINTIFY_URL_BASE}/catalog/print_providers"
    auth_keys = Printify.get_authorization()
    def __init__(self, id_):
        self.url = f"{self.BASE_URL}/{id_}"
        self.id_ = id_

        req = requests.get(f"{self.url}.json", headers=self.auth_keys)
        if not req.ok:
            raise Exception("Failed to get provider with id={id_}")
        self.data = data = req.json()

        self.title = data.get("title", None)
        self.location = Location(data["location"]) if data.get("location", None) else None
        self.images = data.get("images", None)

    def get_shipping_for_product(self, product) -> str:
        url = f"{product.url}/print_providers/{self.id}/shipping.json"
        req = requests.get(url, headers=self.auth_keys)
        if not req.ok:
            raise Exception("Failed to get shipping details for product id={product.id} on provider_id={self.id}")
        data = req.json()
        return data

    def get_variants_for_product(self, product):
        url = f"{product.url}/print_providers/{self.id}/variants.json"
        req = requests.get(url, headers=self.auth_keys)
        if not req.ok:
            raise Exception("Failed to get product with id={product.id} on provider_id={self.id}")
        data = req.json()
        for variant in data.get("variants", {}):
            yield variant.get("id", None)

    @property
    def id(self):
        return self.id_
        
    @classmethod
    def get_all_providers(cls):
        url = f"{cls.BASE_URL}/print_providers.json"
        req = requests.get(url, headers=cls.auth_keys)
        data = req.json()
        return sorted(product["id"] for product in data)

    def __str__(self):
        return f"Provider<id:{self.id_}, title='{self.title}', location={self.location}>"

