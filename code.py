# SPDX-FileCopyrightText: 2020 ladyada, written for Adafruit Industries
#
# SPDX-License-Identifier: Unlicense
import secrets
import time
import json
from adafruit_magtag.magtag import MagTag
import icons

# Change this to the hour you want to check the data at, for us its 7pm
# local time (eastern), which is 19:00 hrs
DAILY_UPDATE_HOUR = 19

try:
    from secrets import secrets
except ImportError:
    print("secrets are kept in secrets.py, please add them there")
    raise

# example secrets.py
# secrets = {
#     'ssid' : '',
#     'password' : '',
#     'aio_username': "",
#     'aio_key': "",
#     'timezone' : "America/New_York",
#     'cdc_app_token' : "",
#     'county_fips_code' : ""
#     }

CDC_API_ID = "3nnm-4jni"
COUNTY_FIPS_CODE = secrets["county_fips_code"]
CDC_API_APP_TOKEN = secrets["cdc_app_token"]
NUMBER_OF_RECORDS = 2


CDC_API_DATA_SOURCE = f"https://data.cdc.gov/resource/{CDC_API_ID}.json?county_fips={COUNTY_FIPS_CODE}&$order=date_updated%20DESC&$limit={NUMBER_OF_RECORDS}"
CDC_API_APP_TOKEN = {"X-App-Token": CDC_API_APP_TOKEN}

magtag = MagTag(
    url=CDC_API_DATA_SOURCE,
    headers=CDC_API_APP_TOKEN,
)

LINE_HEIGHT = 20

LINE_1_Y_POSITION = 10
LINE_2_Y_POSITION = LINE_1_Y_POSITION + LINE_HEIGHT
LINE_3_Y_POSITION = LINE_2_Y_POSITION + LINE_HEIGHT
LINE_4_Y_POSITION = LINE_3_Y_POSITION + LINE_HEIGHT
LINE_5_Y_POSITION = LINE_4_Y_POSITION + LINE_HEIGHT
LINE_6_Y_POSITION = LINE_5_Y_POSITION + LINE_HEIGHT

LEFT_ALIGN_X_POSITION = 10
AFTER_ICON_TEXT_X_POSITION = 30

SECOND_COLUMN_Y_LINE_1_POSITION = 20
SECOND_COLUMN_X_POSITION = 245
SECOND_COLUMN_Y_GAP = 40

# As of date
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(LEFT_ALIGN_X_POSITION, LINE_1_Y_POSITION),
    is_data=False,
)

# County
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(LEFT_ALIGN_X_POSITION, LINE_2_Y_POSITION),
    is_data=False,
)

# Community Level
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(AFTER_ICON_TEXT_X_POSITION, LINE_3_Y_POSITION),
    is_data=False,
)

# Cases
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(AFTER_ICON_TEXT_X_POSITION, LINE_4_Y_POSITION),
    is_data=False,
)

# Inpatient Bed
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(AFTER_ICON_TEXT_X_POSITION, LINE_5_Y_POSITION),
    is_data=False,
)

# Hospital Admissions
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(AFTER_ICON_TEXT_X_POSITION, LINE_6_Y_POSITION),
    is_data=False,
)

# when was the API last called
magtag.add_text(
    text_font="/fonts/Arial-Bold-12.pcf",
    text_position=(SECOND_COLUMN_X_POSITION, SECOND_COLUMN_Y_LINE_1_POSITION),
    line_spacing=0.75,
    is_data=False,
)

# Community Levels
magtag.add_text(
    text_font="/fonts/forkawesome-12.pcf",
    text_position=(LEFT_ALIGN_X_POSITION, LINE_3_Y_POSITION),
    is_data=False,
)

# Cases Icon
magtag.add_text(
    text_font="/fonts/forkawesome-12.pcf",
    text_position=(LEFT_ALIGN_X_POSITION, LINE_4_Y_POSITION),
    is_data=False,
)

# Inpatient Icon
magtag.add_text(
    text_font="/fonts/forkawesome-12.pcf",
    text_position=(LEFT_ALIGN_X_POSITION, LINE_5_Y_POSITION),
    is_data=False,
)

# Hospital Admissions Icon
magtag.add_text(
    text_font="/fonts/forkawesome-12.pcf",
    text_position=(LEFT_ALIGN_X_POSITION, LINE_6_Y_POSITION),
    is_data=False,
)


def fetch_covid_data():
    print("fetching data")

    now = time.localtime()
    print("Now: ", now)

    raw_data = json.loads(magtag.fetch(auto_refresh=False))

    output_values = {}

    output_values["date_updated"] = raw_data[0]["date_updated"][0:10]

    output_values["api_last_called"] = "%d/%d\n%d:%02d" % now[1:5]

    output_values["county"] = raw_data[0]["county"]
    
    current_community_level = raw_data[0]["covid_19_community_level"]
    prior_value_community_level = raw_data[1]["covid_19_community_level"]

    output_values["community_level"] = current_community_level

    current_community_level = current_community_level.lower()
    prior_value_community_level = prior_value_community_level.lower()

    if current_community_level == "low" and (prior_value_community_level == "medium" or prior_value_community_level == "high"):
         output_values["community_level_direction"] = "down"
    elif current_community_level == "medium" and (prior_value_community_level == "low"):
         output_values["community_level_direction"] = "up"
    elif current_community_level == "medium" and (prior_value_community_level == "high"):
         output_values["community_level_direction"] = "down"
    elif current_community_level == "high" and (prior_value_community_level == "low" or prior_value_community_level == "medium"):
         output_values["community_level_direction"] = "up"
    
    current_cases_per_100k = raw_data[0]["covid_cases_per_100k"]
    prior_cases_per_100k = raw_data[1]["covid_cases_per_100k"]

    output_values["cases_per_100k"] = current_cases_per_100k

    if current_cases_per_100k > prior_cases_per_100k:
        output_values["cases_per_100k_direction"] = "up"
    elif current_cases_per_100k < prior_cases_per_100k:
        output_values["cases_per_100k_direction"] = "down"

    current_inpatient_bed_utilization = raw_data[0]["covid_inpatient_bed_utilization"]
    prior_inpatient_bed_utilization = raw_data[1]["covid_inpatient_bed_utilization"]

    output_values["inpatient_bed_utilization"] = current_inpatient_bed_utilization

    if current_inpatient_bed_utilization > prior_inpatient_bed_utilization:
        output_values["inpatient_bed_utilization_direction"] = "up"
    elif current_inpatient_bed_utilization < prior_inpatient_bed_utilization:
        output_values["inpatient_bed_utilization_direction"] = "down"

    current_hospital_admissions_per_100k = raw_data[0]["covid_hospital_admissions_per_100k"]
    prior_hospital_admissions_per_100k = raw_data[1]["covid_hospital_admissions_per_100k"]

    output_values["hospital_admissions_per_100k"] = current_hospital_admissions_per_100k

    if current_hospital_admissions_per_100k > prior_hospital_admissions_per_100k:
        output_values["hospital_admissions_per_100k_direction"] = "up"
    elif current_hospital_admissions_per_100k < prior_hospital_admissions_per_100k:
        output_values["hospital_admissions_per_100k_direction"] = "down"

    return output_values

def direction_icon(direction_text):
    icon = ""
    if direction_text == "up":
        icon = icons.chevron_circle_up
    elif direction_text == "down":
        icon = icons.arrow_down
    else:
        icon = icons.circle_o
    return icon

def capitalize(input_string):
    output = ""
    if len(input_string) > 0:
        output = input_string[0].upper() + input_string[1:].lower()
    return output

def update_labels(values):
    # Set the labels for the current game data
    magtag.set_text(f"As of: {values['date_updated']}", 0, False)
    magtag.set_text(f"{values['county']}", 1, False)
    magtag.set_text(f"Community Level: {capitalize(values['community_level'])}", 2, False)
    magtag.set_text("Cases/100k: {0:,}".format(values['cases_per_100k']), 3, False)
    magtag.set_text(f"Inpatient Bed: {values['inpatient_bed_utilization']}", 4, False)
    magtag.set_text(f"Admissions/100k: {values['hospital_admissions_per_100k']}", 5, False)
    magtag.set_text(f"{values['api_last_called']}", 6, False)
    
    magtag.set_text(direction_icon(values.get("community_level_direction")), 7, False)
    magtag.set_text(direction_icon(values.get("cases_per_100k_direction")), 8, False)
    magtag.set_text(direction_icon(values.get("inpatient_bed_utilization_direction")), 9, False)
    magtag.set_text(direction_icon(values.get("hospital_admissions_per_100k_direction")), 10, False)

    magtag.graphics.qrcode(b"https://www.cdc.gov/coronavirus/2019-ncov/science/community-levels.html", qr_size=1, x=SECOND_COLUMN_X_POSITION, y=SECOND_COLUMN_Y_LINE_1_POSITION + SECOND_COLUMN_Y_GAP)

    magtag.refresh()
    # wait 2 seconds for display to complete
    time.sleep(2)


magtag.peripherals.neopixels.brightness = 0.1
magtag.peripherals.neopixel_disable = False  # turn on lights
magtag.peripherals.neopixels.fill(0x0F0000)  # red!

magtag.get_local_time()

try:
    output = fetch_covid_data()
    update_labels(output)
    # OK we're done!
    magtag.peripherals.neopixels.fill(0x000F00)  # greten
except (ValueError, RuntimeError) as e:
    print("Some error occured, trying again later -", e)

time.sleep(2)  # let screen finish updating

now = time.localtime()

# we only wanna wake up once a day, around the event update time:
event_time = time.struct_time(
    (now[0], now[1], now[2], DAILY_UPDATE_HOUR, 0, 0, -1, -1, now[8])
)
# how long is that from now?
remaining = time.mktime(event_time) - time.mktime(now)
if remaining < 0:  # ah its aready happened today...
    remaining += 24 * 60 * 60  # wrap around to the next day
remaining_hrs = remaining // 3660
remaining_min = (remaining % 3600) // 60
print("Gonna zzz for %d hours, %d minutes" % (remaining_hrs, remaining_min))

# Turn it all off and go to bed till the next update time
magtag.exit_and_deep_sleep(remaining)
