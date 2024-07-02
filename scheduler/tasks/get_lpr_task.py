import re
from libs.eocortex import EocortexManager
from libs.moment import convert_timeutc_to_timestamp
from datetime import datetime
from cctv.models import Camera
from activity.models import LPR, Vehicle


def format_numberplate(numberplate):
    # Remove any non-alphanumeric characters
    cleaned_numberplate = re.sub(r"\W+", "", numberplate)

    # Find the position where the digit ends in the cleaned numberplate
    for i, char in enumerate(cleaned_numberplate):
        if char.isdigit() and (
            i == len(cleaned_numberplate) - 1
            or not cleaned_numberplate[i + 1].isdigit()
        ):
            break
    # Format the cleaned numberplate
    return f"{cleaned_numberplate[0]}-{cleaned_numberplate[1:i + 1]}-{cleaned_numberplate[i + 1:]}"


def get_lpr_task(start_ts: datetime, end_ts: datetime):
    print("running get_lpr_task.....")
    em = EocortexManager()

    try:
        print("getting channels....")
        channels = em.get_channels()
    except Exception as err:
        channels = []
        print({"action": "get channel eocortex", "error": str(err)})

    for channel in channels:
        channel_id = channel["id"]
        camera = Camera.objects.filter(channel_id=channel_id).last()

        # skip if exists record
        try:
            print("get lpr for channel: ", channel_id)
            lpr_results = em.get_result_lpr(start_ts, end_ts, channel_id)
        except Exception as err:
            lpr_results = []
            print(
                {
                    "action": "get lpr channel: " + channel_id,
                    "error": str(err),
                    "data": {
                        "start_ts": start_ts,
                        "end_ts": end_ts,
                        "channel_id": channel_id,
                    },
                }
            )

        for result in lpr_results:
            direction = result["Direction"]
            time_utc = result["TimeUtc"]
            time_utc_ts = convert_timeutc_to_timestamp(time_utc)
            number_plate = result["Numberplate"]
            number_plate_parsed = format_numberplate(number_plate)
            exists_vehicle = Vehicle.objects.filter(
                license_plate_number=number_plate_parsed
            ).last()

            search_criteria = {
                "number_plate": number_plate_parsed,
                "direction": direction,
                "time_utc_timestamp": time_utc_ts,
                "channel_id": channel_id,
            }

            # Define the defaults for creation or update
            defaults = {"camera": camera, "vehicle": exists_vehicle}

            # Use update_or_create to find and update, or create a new entry
            LPR.objects.update_or_create(defaults=defaults, **search_criteria)

    print("get_lpr_task has finish.....")
