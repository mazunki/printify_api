
import os, sys
import requests as req
import json

class Printify:
    PRINTIFY_URL_BASE="https://api.printify.com/v1"

    @classmethod
    def get_authorization(cls):
        API_TOKEN=os.getenv("PRINTIFY_API_TOKEN")
        return {"Authorization": f"Bearer {API_TOKEN}"}

