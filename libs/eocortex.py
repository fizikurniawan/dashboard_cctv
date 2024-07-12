import requests
import json
import base64
from datetime import datetime
from common.models import Configuration
from cctv.models import Camera


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

    def get_result_lpr_v2(self, start_ts: datetime, end_ts: datetime) -> dict:
        url = self.base_url + "/archive_events"
        start_time = start_ts.strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
        finish_time = end_ts.strftime("%d.%m.%Y %H:%M:%S.%f")[:-3]
        body = {
            "startTimeUtc": start_time,
            "endTimeUtc": finish_time,
            "cameraIds": [i.channel_id for i in Camera.objects.filter()],
            "eventCategories": [0, 1, 2],
            "eventInitiatorTypes": [0, 2, 8, 4, 1, 3],
            "eventInitiators": ["91baab3e-ef9d-48c6-b803-2e70f4475960"],
            "eventIds": [
                "5a692f4d-bf82-49cd-ae72-5de4660b8bfb",
                "c9d6d086-c965-4cf8-aef6-85b3894e3a4a",
            ],
            "isSearchFromBegin": False,
            "searchLimitCount": 200,
        }

        try:
            response = requests.post(
                url, json=body, headers={"Authorization": "Basic cm9vdDo="}
            )
            response.raise_for_status()

            try:
                return response.json()
            except json.JSONDecodeError:
                response.encoding = "utf-8-sig"
                return response.json()

        except Exception as e:
            print({"error": "request failed", "body": body, "err": str(e)})

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

    def get_specialarchiveevents(
        self,
        start_ts: datetime,
        end_ts: datetime,
        eventid: str = "c9d6d086-c965-4cf8-aef6-85b3894e3a4a",
    ):
        url = self.base_url + "/specialarchiveevents"
        start_time = start_ts.strftime("%d.%m.%Y %H:%M:%S")
        finish_time = end_ts.strftime("%d.%m.%Y %H:%M:%S")
        params = {
            "login": "root",
            "password": None,
            "responsetype": "json",
            "eventid": eventid,
            "starttime": start_time,
            "endtime": finish_time,
        }
        response = requests.get(url, params=params)

        content_text = response.content.decode("utf-8-sig")
        if response.status_code != 200:
            raise Exception(content_text)

        # remove all unneded text
        content_text = content_text.replace("\r\n\t", "").replace("\r\n", "")
        json_strings = content_text.split("}{")
        json_strings = [
            s + "}" if not s.endswith("}") else "{" + s for s in json_strings
        ]

        json_object = []
        for s in json_strings:
            json_st = s
            if not s.endswith("}"):
                json_st = json_st + "}"

            if not s.startswith("{"):
                json_st = "{" + json_st
            json_object.append(json.loads(json_st))

        return json_object
