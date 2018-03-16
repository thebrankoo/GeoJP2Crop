"""This module process location data."""
import json
import requests

URL_PRE = "https://exxo:exxopass123@"

class LocationRequester(object):
    """This class fetches and parses santinel location data."""
    target_url = ""

    base_download_url = ""
    base_preview_url = ""
    location_summary = ""
    product_id = ""
    product_title = ""

    def __init__(self, requestURL):
        self.target_url = requestURL

    def request_location(self):
        """request_location(self) -> requests location satellite images as json"""
        response = requests.get(self.target_url)
        return response.json()

    def parse_request_json(self):
        """parse_request_json(self) - parses json form url and returns in mail format"""
        mail_text = ""

        json_data = self.request_location()
        json_encoded = json.dumps(json_data)
        json_decoded = json.loads(json_encoded)

        for value in json_decoded["feed"]["entry"]:
            self.product_title = value["title"]
            self.location_summary = value["summary"]
            self.product_id = value["id"]

            for lst in value['link']:
                if "rel" in lst:
                    if lst["rel"] == "icon":
                        self.base_preview_url = lst["href"]
                else:
                    self.base_download_url = lst["href"]

                download_url = URL_PRE + self.base_download_url[8:]
                preview_url = URL_PRE + self.base_preview_url[8:]
                loc_summary_text = "Location summary: " + self.location_summary + "\n"
                loc_preview_text = "Access location preview: " + preview_url + "\n"
                loc_url_text = "Download location: " + download_url + "\n"
                mail_text += loc_summary_text + loc_preview_text + loc_url_text
                mail_text += "=================================\n"

        return mail_text

URL_BASE = "scihub.copernicus.eu/dhus/search?"
URL_PARAMS1 = 'q=(platformname:Sentinel-2)'
URL_PARAMS2 = '%20AND%20footprint:"Intersects'
URL_PARAMS3 = '(POLYGON((19.83%2043.27,21.66%2043.29,21.64%2042.65,20.45%2042.67,19.83%2043.27)))"'
URL_PARAMS4 = '&format=json'

URL_FULL = URL_PRE + URL_BASE + URL_PARAMS1 + URL_PARAMS2 + URL_PARAMS3 + URL_PARAMS4
LOC_REQ = LocationRequester(URL_FULL)

print LOC_REQ.parse_request_json()
