#!/usr/bin/env python
from printify import Printify
from providers import Provider
import requests, json

class Shipping(Printify):
    class Money:
        def __init__(self, amount, currency):
            self.amount = amount/100
            self.currency = currency
        def __str__(self):
            return f"{self.amount} {self.currency}"

        def __format__(self, fmt):
            return fmt.format(self.currency) + " USD"

    class Profile:
        def __init__(self, profile: dict):
            self.variants = profile.get("variant_ids", [])
            self.first_item = profile.get("first_item", {})
            self.additional_items = profile.get("additional_items", {})
            self.countries = profile.get("countries", [])

        @property
        def cost(self):
            return Shipping.Money(self.first_item.get("cost"), self.first_item.get("currency"))

        def __contains__(self, other):
            return other in self.countries or "REST_OF_THE_WORLD" in self.countries

        def __str__(self):
            return f"{self.cost} ({len(self.variants)} variants)"


    def __init__(self, shipping: dict):
        self.data = shipping
        self._handling_time = self.data.get("handling_time", {})
        self.profiles = { Shipping.Profile(p) for p in self.data.get("profiles", {}) }
        
    def profiles_in_country(self, country_code):
        return [ profile for profile in self.profiles if country_code in profile ]

    @property
    def handling_time(self):
        time = self._handling_time.get("value", 0)
        unit = self._handling_time.get("unit", "timeunits")
        return f"{time} {unit}"

    def __str__(self):
        return str(self.profiles)

    def __iter__(self):
        for profile in self.profiles:
            yield profile

class Product(Printify):
    BASE_URL = f"{Printify.PRINTIFY_URL_BASE}/catalog"
    auth_keys = Printify.get_authorization()
    def __init__(self, id_):
        self.url = f"{self.BASE_URL}/blueprints/{id_}"
        self.id = id_
        self._providers = None
        self._blueprint = None
        self._variants = None
        self._shipping = None

        req = requests.get(f"{self.url}.json", headers=self.auth_keys)
        self.data = data = req.json()

        self.title = data.get("title", None)
        if not self.title:
            raise Warning(f"No title found for item with id={self.id}")

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
        return self._providers


    def is_available_in(self, country_code):
        for shipper in self.shipping.values():
            if shipper.profiles_in_country(country_code):
                return True
        return False

    def providers_in(self, country_code):
        providers = set()
        for provider, shipping_details in self.shipping.items():
            if shipping_details.profiles_in_country(country_code):
                providers.add((provider, shipping_details))
        return providers


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
        return self._variants

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
        return f"Product<id:{self.id}, title:'{self.title}', brand:'{self.brand}', self.model:'{self.model}', variants:{variants_s}, providers:{provider_s}>"

