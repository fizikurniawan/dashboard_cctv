import requests
import json
import base64
import hashlib
from datetime import datetime
from common.models import Configuration, File
from cctv.models import Camera
from activity.models import LPR
from django.conf import settings
from django.core.files.base import ContentFile
import urllib


EOCORTEX_USER = getattr(settings, "EOCORTEX_USER", "root")
EOCORTEX_PASS = getattr(settings, "EOCORTEX_PASS", "")


class EocortexManager(object):
    def __init__(self) -> None:
        self.base_url = self.get_base_url()
        self.user = EOCORTEX_USER
        self.password = hashlib.md5(EOCORTEX_PASS.encode()).hexdigest()

    def get_credentials(self):
        credentials = f"{self.user}:{self.password}"
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
            response = requests.post(url, json=body, headers=self.get_credentials())
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
            "responsetype": "json",
            "eventid": eventid,
            "starttime": start_time,
            "endtime": finish_time,
        }
        response = requests.get(url, params=params, headers=self.get_credentials())

        content_text = response.content.decode("utf-8-sig")
        if response.status_code != 200:
            raise Exception(content_text)

        # remove all unneded text
        content_text = content_text.replace("\r\n\t", "").replace("\r\n", "")
        json_strings = content_text.split("}{")

        json_object = []
        for s in json_strings:
            json_st = s
            if not s.endswith("}"):
                json_st = json_st + "}"

            if not s.startswith("{"):
                json_st = "{" + json_st

            if json_st == "{}":
                continue
            json_object.append(json.loads(json_st))

        print(
            {
                "action": "LOG",
                "action": "response eocortex",
                "raw_resp": response.content,
                "parse_json": json_object,
            }
        )

        return json_object

    def get_lpr_sn(self, channel_id: str, lpr_instance: LPR):
        url = self.base_url + "/site"
        params = {
            "resolutionx": 1920,
            "resolutiony": 1080,
            "oneframeonly": True,
            "withcontenttype": True,
            "mode": "archive",
            "startTime": lpr_instance.time_utc_str_get_sn,
            "channelid": channel_id,
        }
        response = requests.get(url, params=params, headers=self.get_credentials())

        file_name = f"sn_lpr_{lpr_instance.number_plate}_{lpr_instance.id}.jpg"
        file_content = ContentFile(response.content, file_name)
        file_instance = File.objects.create(
            name=file_name, file=file_content, content_object=lpr_instance
        )

        return file_instance
    
    def send_ptz_command(self, command, params):
        url = f"{self.base_url}/ptz?command={command}&login={self.user}&password={self.password}"
        url += ''.join([f"&{key}={value}" for key, value in params.items()])
        response = requests.get(url, headers=self.get_credentials())
        response.raise_for_status()
        return response.text

    def get_ptz_capabilities(self, channel_id):
        params = {'channelid': channel_id, 'responsetype': 'json'}
        return self.send_ptz_command('getcapabilities', params)

    def continuous_move(self, channel_id, pan_speed=0, tilt_speed=0, stop_timeout=500):
        params = {
            'channelid': channel_id,
            'panspeed': pan_speed,
            'tiltspeed': tilt_speed,
            'stoptimeout': stop_timeout
        }
        return self.send_ptz_command('startmove', params)

    def stop_movement(self, channel_id):
        params = {'channelid': channel_id}
        return self.send_ptz_command('stop', params)

    def step_zoom(self, channel_id, zoom_step):
        params = {'channelid': channel_id, 'zoomstep': zoom_step}
        return self.send_ptz_command('zoom', params)

    def continuous_zoom(self, channel_id, speed, stop_timeout=500):
        params = {
            'channelid': channel_id,
            'speed': speed,
            'stoptimeout': stop_timeout
        }
        return self.send_ptz_command('startzoom', params)

    def set_preset(self, channel_id, index):
        params = {'channelid': channel_id, 'index': index}
        return self.send_ptz_command('gotopreset', params)

    def auto_focus(self, channel_id):
        params = {'channelid': channel_id}
        return self.send_ptz_command('setautofocus', params)

    def center_camera(self, channel_id, width, height, x, y):
        params = {
            'channelid': channel_id,
            'width': width,
            'height': height,
            'x': x,
            'y': y
        }
        return self.send_ptz_command('moveto', params)