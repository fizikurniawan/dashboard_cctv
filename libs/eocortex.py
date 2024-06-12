import requests
import json
from common.models import Configuration


class EocortexManager(object):
    def __init__(self) -> None:
        self.base_url = self.get_base_url()

    def get_base_url(self):
        config = Configuration.objects.filter(key="EOCORTEX_URL").first()
        return getattr(config, "value", None)

    def get_channels(self):
        url = self.base_url + "/configex"
        params = {"login": "root", "password": None, "responsetype": "json"}
        response = requests.get(url, params=params)
        channels = response.json()["Channels"]
        channels_map = [{"id": i["Id"], "name": i["Name"]} for i in channels]
        return channels_map

    def get_result_lpr(self, start_ts, end_ts, channelId):
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
