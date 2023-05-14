#!/usr/bin/env python
from printify import Printify
from providers import Provider
import requests, json

class Shipping(Printify):
    def __init__(self, shipping: dict):
        self.data = shipping
        self.handling_time = self.data.get("handling_time", None)
        self.profiles = self.data.get("profiles") or {}
        
    def profiles_in_country(self, country_code):
        return [
                profile
                for profile in self.profiles
                if country_code in profile.get("countries")
                    or "REST_OF_THE_WORLD" in profile.get("countries")
            ]

    def __str__(self):
        return str(self.profiles)

class Product(Printify):
    BASE_URL = f"{Printify.PRINTIFY_URL_BASE}/catalog"
    auth_keys = Printify.get_authorization()
    def __init__(self, id_):
        self.url = f"{self.BASE_URL}/blueprints/{id_}"
        self.id_ = id_
        self._providers = None
        self._blueprint = None
        self._variants = None
        self._shipping = None

        req = requests.get(f"{self.url}.json", headers=self.auth_keys)
        self.data = data = req.json()

        self.title = data.get("title", None)
        if not self.title:
            raise Warning(f"No title found for item with id={id_}")
        self.description = data.get("description", None)
        self.brand = data.get("brand", None)
        self.model = data.get("model", None)
        self.images = data.get("images", None)

    def fetch_data(self):
        _ = self.variants
        _ = self.providers
        _ = self.shipping

    @property
    def providers(self):
        if self._providers:
            return self._providers

        req = requests.get(f"{self.url}/print_providers.json", headers=self.auth_keys)
        if not req.ok:
            raise Exception("Failed to get providers")
        data = req.json()
        self._providers = set()
        for provider in data:
            provider = Provider(provider["id"])
            self._providers.add(provider)
            yield provider

    @property
    def shipping(self):
        if self._shipping:
            return self._shipping

        self._shipping = dict()
        for provider in self.providers:
            shipping = provider.get_shipping_for_product(self)
            self._shipping[provider] = Shipping(shipping)

        return self._shipping

    @property
    def variants(self):
        if self._variants:
            return self._variants

        self._variants = set()
        for provider in self.providers:
            for variant in provider.get_variants_for_product(self):
                self._variants.add(variant)
                yield variant

    def __iter__(self):
        for item in self.variants:
            yield item

    @classmethod
    def get_all_product_ids(cls):
        url = f"{cls.BASE_URL}/print_providers.json"
        req = requests.get(url, headers=cls.auth_keys)
        data = req.json()
        return sorted(product["id"] for product in data)

    def __str__(self):
        provider_s = f"{{{len(self._providers)} Provider...}}" if self._providers is not None else "{? Provider...}"
        variants_s = f'{{{len(self._variants)} id...}}' if self._variants is not None else "{? id...}"
        return f"Product<id:{self.id_}, title:'{self.title}', brand:'{self.brand}', self.model:'{self.model}', variants:{variants_s}, providers:{provider_s}>"

