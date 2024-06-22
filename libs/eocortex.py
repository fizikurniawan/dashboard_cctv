import requests
import json
import base64
from datetime import datetime
from common.models import Configuration


class EocortexManager(object):
    def __init__(self) -> None:
        self.base_url = self.get_base_url()

    def get_credentials(self):
        login = "root"
        password = ""
        credentials = f"{login}:{password}"
        encoded_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {"Authorization": f"Basic {encoded_credentials}"}

        return headers

    def get_base_url(self):
        config = Configuration.objects.filter(key="EOCORTEX_URL").first()
        return getattr(config, "value", None)

    def get_channels(self):
        url = self.base_url + "/configure/channels"
        response = requests.get(url, headers=self.get_credentials())
        channels_map = [{"id": i["Id"], "name": i["Name"]} for i in response.json()]
        return channels_map

    def get_cars(self):
        url = self.base_url + "/api/cars"
        response = requests.get(url, headers=self.get_credentials())
        return response.json()

    def get_result_lpr(
        self, start_ts: datetime, end_ts: datetime, channelId: str
    ) -> dict:
        url = self.base_url + "/autovprs_export"
        start_time = start_ts.strftime("%Y-%m-%d-%H-%M-%S-%f")
        finish_time = end_ts.strftime("%Y-%m-%d-%H-%M-%S-%f")

        def get_3_ms(ts_str):
            date_time_parts = ts_str.split("-")
            date_time_parts[-1] = date_time_parts[-1][:3]
            return "-".join(date_time_parts)

        start_time = get_3_ms(start_time)
        finish_time = get_3_ms(finish_time)
        params = {
            "login": "root",
            "password": None,
            "responsetype": "json",
            "startTime": start_time,
            "finishTime": finish_time,
            "channelId": channelId,
            "content-type": "application/json",
        }

        try:
            response = requests.get(url, params=params)
            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                response.encoding = "utf-8-sig"
                return response.json()

        except Exception as e:
            print("Request failed:", e)

    def get_registered_events(self):
        url = self.base_url + "/command"
        params = {
            "login": "root",
            "password": None,
            "responsetype": "json",
            "type": "getallregisteredevents",
        }
        response = requests.get(url, params=params)
        json_start = response.text.find("[")
        json_part = response.text[json_start:]
        data = json.loads(json_part)

        return [{"id": i["Id"], "name": i["GuiName"]} for i in data]

    def get_events(self):
        url = self.base_url + "/event"
        params = {
            "login": "root",
            "password": None,
            "responsetype": "json",
            "filter": "57acfc1e-7420-4e4c-9b4f-eebd1950e2e8",
        }
        response = requests.get(url, params=params)
        json_start = response.text.find("[")
        json_part = response.text[json_start:]
        data = json.loads(json_part)

        return data