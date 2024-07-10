import re
import traceback
from libs.eocortex import EocortexManager
from datetime import datetime
from cctv.models import Camera
from activity.models import LPR, Vehicle


def extract_number_plate(text):
    # Use regex to find the number plate in the text
    # match = re.search(r"\b[A-Z0-9]+\b", text)
    match = re.search(
        r"Numberplate recognised: (.*?)\.License Plate Recognition \(Complete\)\.",
        text,
    )

    if match:
        return match.group(1)
    return None


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
    print("running get_lpr_task_v2.....")
    em = EocortexManager()

    try:
        lpr_results = em.get_result_lpr_v2(start_ts, end_ts)
    except Exception as err:
        lpr_results = []
        print(
            {
                "action": "get lpr data from archive_events",
                "error": str(err),
                "data": {
                    "start_ts": start_ts,
                    "end_ts": end_ts,
                },
            }
        )

    for result in lpr_results:
        channel_id = result["ChannelId"]
        camera_name = result["ChannelName"]
        camera = Camera.objects.filter(channel_id=channel_id).first()
        if not camera:
            camera = Camera.objects.create(name=camera_name, channel_id=channel_id)

        number_plates_recognized = result["EventComment"]
        extracted_number_plate = extract_number_plate(number_plates_recognized)

        if not extracted_number_plate:
            continue

        number_plate_parsed = format_numberplate(extracted_number_plate)
        exists_vehicle = Vehicle.objects.filter(
            license_plate_number=number_plate_parsed
        ).last()

        time_utc_ts = int(
            datetime.fromisoformat(
                result["Timestamp"].replace("Z", "+00:00")
            ).timestamp()
            * 1000
        )

        search_criteria = {
            "number_plate": number_plate_parsed,
            "direction": "Unknown",
            "time_utc_timestamp": time_utc_ts,
            "channel_id": channel_id,
        }

        # Define the defaults for creation or update
        defaults = {"camera": camera, "vehicle": exists_vehicle}

        # Use update_or_create to find and update, or create a new entry
        try:
            LPR.objects.update_or_create(defaults=defaults, **search_criteria)
        except Exception as err:
            print(
                {
                    "message": "Failed create LPR",
                    "error": str(err),
                    "traceback": traceback.format_exc(),
                }
            )

    print("get_lpr_task_v2 has finish.....")