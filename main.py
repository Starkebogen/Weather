"""=====================================================================================================================

Title              Weather Forecast

Description        Generates an hourly weather forecast for the next 48 hours and a daily summary the next 7 days for
                   each of the locations specified in the file "locations_data.json".

Background         Inspired by the Day 35 exercise in Doctor Angela Yu's excellent Python course "100 Days of Code -
                   The Complete Python Pro Bootcamp for 2021", which is available on www.udemy.com.  The difference
                   between this program and the course exercise is that this program produces daily and hourly weather
                   reports for several locations, whereas the course exercise sends a single SMS alert advising whether
                   rain (or snow) is expected within the next twelve hours for a single location.

Author             Max Parry

Date               14 March 2021

Notes              The forecast data is retrieved from the website www.openweathermap.org via that site's api

                   Date and time processing is not straightforward because we are dealing with several time zones and
                   date/time formats:  All api dates and times are in UTC time in seconds since 1/1/1970 (UNIX format);
                   System time is in CET (CEST when summer time is in effect);  All output dates and times are in the
                   local time of the location being reported on.  Comments and variable names in the program use the
                   term "location time" when referring to the local time of the location being processed and "system
                   time" when referring to the time of the computer clock.  N.B. UTC does NOT change when Summer Time
                   is in effect.  Summer Time is reflected in timezone_offset returned by the api.

Portability        The program was written for the author's personal use.  It uses the author's openweathermap account,
                   relies on system time being in the author's time zone normal (CET/CEST) and reports on locations
                   selected by the author.

                   Users other than the author should ensure these points are addressed:

                       1) An openweathermap.org api account is required.  The api key of the account should be stored 
                          in a text file named "api_key.txt" in the same folder as the source code file "main.py"

                       2) The location(s) to be reported on should be detailed in a text file "location_data.json" in
                          the same folder as the source code file "main.py"

                       3) The variable SYSTEM_TIME_UTC_OFFSET should contain the difference between system time and UTC

Amendment History  15 March 2021 Wind speed reported in kilometres per hour (kph) rather than metres per second
                   16 March 2021 Index j changed to i in "for j in range(0, HOURS)" and "for j in range(0, DAYS)"
                   29 March 2021 Handling of summer time (DST) simplified by using tm_isdst
                   30 March 2021 The user id for the openweathermap.org account moved from the source code to the file
                                 "api_key.txt" and containing variable name changed from API_ID to api_key
                    3 May 2021   Kesten added to locations()
                    4 May 2021   Tuple LOCATIONS changed to a list and renamed locations as a precursor to holding
                                 location data in a file
                    6 May 2021   Daily report output amended to put prevailing conditions and wind speed on the same
                                 line, thus enabling report to fit on a single page
                   20 May 2021   Data of the location(s) moved to an external json file from where it is loaded into
                                 the list locations
                   21 May 2021   Comments tidied
                    1 June 2021  File name addedd to Description comment
                    6 June 2021  Elapsed execution time reported

====================================================================================================================="""
import requests
from datetime import *
import time
import json

# Tell the world what we are about to start and record the start time
print()                                                                                   # blank line before any output
print("***** Weather Forecast program is starting *****")                               # Tell the world we are starting
print()
start_time = time.time()

# Constants
OWM_API_URL = "https://api.openweathermap.org/data/2.5/onecall"                            # openweathermap api endpoint

HOURS = 48                                                              # Number of hours we produce hourly forecast for
DAYS = 8                                                                     # Number of days produce daily forecast for
SYSTEM_TIME_UTC_OFFSET = 3600        # System time is CET which is one hour ahead of UTC (value is expressed in seconds)

# Get target locations
with open("locations_data.json") as f:
    locations = json.load(f)                           # We can view locations in a json viewer e.g. jsonviewer.stack.hu
    # print(locations)   # To export the locations data for viewing in a json viewer we will need to uncomment this line

# Get openweathermap account id
with open("api_key.txt", "r") as f:
    api_key = f.read()

# Detect and cater for summer time
system_time = time.localtime()                                                              # System time is CET or CEST
if system_time.tm_isdst != 0:                                                               # Summertime (DST) in effect
    SYSTEM_TIME_UTC_OFFSET = SYSTEM_TIME_UTC_OFFSET + 3600          # Increase offset by one hour (expressed in seconds)

# Create prefix for output file names (file names will be YYYY_MM_DD_location_frequency_Forecast.txt)
today = date.today()                                                              # Today's date (for use in file names)
file_name_prefix = today.strftime("%Y") + "_" + today.strftime("%m") + "_" + today.strftime("%d") + "_"    # YYYY_MM_DD_
file_name_suffix = "_Forecast.txt"  # Place (location) and frequency (hourly or daily) will go between prefix and suffix

# Process each location
for location in locations:

    # Get forecast data for current location via openweathermap api
    api_parameters = {
        "lat": location["Latitude"],
        "lon": location["Longitude"],
        "exclude": "current,minutely,alerts",               # We are only interested in hourly and daily data and alerts
        "units": "metric",
        "lang": location["Language"],
        "appid": api_key
    }
    response = requests.get(OWM_API_URL, params=api_parameters)                                             # Invoke api
    response.raise_for_status()                                                                   # Handle any API error
    api_data = response.json()                          # We can view api_data in a json viewer e.g. jsonviewer.stack.hu
    # print(api_data)          # To export the api data for viewing in a json viewer we will need to uncomment this line

    # Get current location time and format for use as file/report generated time in file/report headings
    location_time_offset = (api_data["timezone_offset"] - SYSTEM_TIME_UTC_OFFSET) / 3600  # Location time offset (hours)
    location_time = datetime.now() + timedelta(hours=location_time_offset)   # Location time calculated from system time
    files_generated_time = location_time.strftime("%H:%M")               # Convert location time to print format (HH:MM)

    # Literal to describe UTC Offset in both hourly and daily report headings
    if abs(api_data["timezone_offset"]) == 3600:                         # Is this location one hour ahead or behind UTC
        UTC_hours_literal = "hour"                                    # Plus or minus one hour so we use singular "hour"
    else:
        UTC_hours_literal = "hours"      # Not one hour different (i.e. zero or multiple hours) so we use plural "hours"

    # Create hourly forecast file for this location
    file_name = file_name_prefix + location["Place"] + "_Hourly" + file_name_suffix     # Create hourly report file name
    with open(file_name, "w", encoding="utf-8") as f:

        # Output hourly file/report heading
        f.write(f"{location['Place']} Hourly Forecast.  Generated at {files_generated_time} local time ")
        f.write(f"(UTC Offset: {round(api_data['timezone_offset'] / 3600)} {UTC_hours_literal})\n\n")       # UTC Offset

        # Starting/default values for file/report summary
        rain_or_snow_predicted = False                                # When we start we assume no rain or snow expected
        min_temp = api_data["hourly"][0]["temp"]  # Start with the minimum temperature set to the first hour temperature
        max_temp = api_data["hourly"][0]["temp"]  # Start with the maximum temperature set to the first hour temperature

        # Process each hour
        for i in range(0, HOURS):            # We are looking at the data for the next required number of hours (max 48)

            # Produce hourly snapshot report heading
            location_time = api_data["hourly"][i]["dt"]                  # Extract date and time (UTC time, Unix format)
            location_time = location_time + api_data["timezone_offset"]                          # Adjust for UTC Offset
            location_time = location_time - SYSTEM_TIME_UTC_OFFSET                       # Adjust for system time offset
            print_time = datetime.fromtimestamp(location_time).strftime("%a %e %B %Y, %H:%M")
            f.write(f'{print_time}\n')                                                                   # Date and time

            # Produce hourly report snapshot
            wind_speed = round(api_data["hourly"][i]["wind_speed"] / 1000 * 3600)   # Convert wind speed from mps to kph
            f.write(f'    Temperature {round(api_data["hourly"][i]["temp"]): >2}°C ('                      # Temperature
                    f'feels like {round(api_data["hourly"][i]["feels_like"]): >2}°C), '                     # Feels like
                    f'wind speed {wind_speed: >3}kph, '                                                     # Wind speed
                    f'{api_data["hourly"][i]["weather"][0]["description"]}\n\n')     # Prevailing weather and blank line

            # Update report summary if necessary
            if int(api_data["hourly"][i]["weather"][0]["id"]) < 700:   # Below 700 indicates rain (or snow) of some type
                rain_or_snow_predicted = True                    # We've changed our mind:  rain (or snow) now predicted

            # If necessary, adjust minimum and maxim temperatures for summary
            if api_data["hourly"][i]["temp"] < min_temp:                         # If there is a new minimum temperature
                min_temp = api_data["hourly"][i]["temp"]                                                     # Record it
            if api_data["hourly"][i]["temp"] > max_temp:                         # If there is a new maximum temperature
                max_temp = api_data["hourly"][i]["temp"]                                                     # Record it

        # We have processed all the required hours so we generate summary for ths location
        # This summary is the nearest we come to the solution to Angela's Day 35 Exercise (which is an SMS message)!
        f.write(f"\n")                                                                       # Blank line before summary
        f.write(f"Summary: Minimum temperature: {round(min_temp)}°C, maximum {round(max_temp)}°C, ")      # Temperatures
        if rain_or_snow_predicted:                                                   # Is rain (or snow) predicted today
            f.write("Rain (or snow) expected!\n")                                                # Yes, tell our readers
        else:
            f.write("No rain expected!\n")                                         # No, tell our readers it will be dry

    # Create daily forecast file for this location
    file_name = file_name_prefix + location["Place"] + "_Daily" + file_name_suffix       # Create daily report file name
    with open(file_name, "w", encoding="utf-8") as f:

        # Output daily file/report heading
        f.write(f"{location['Place']} Daily Forecast.  Generated at {files_generated_time} local time "
                f"(UTC Offset: {round(api_data['timezone_offset'] / 3600)} {UTC_hours_literal})\n\n")       # UTC Offset

        # Process each day
        for i in range(0, DAYS):               # We are looking at the data for the next required number of days (max 8)

            print_date = datetime.fromtimestamp(api_data["daily"][i]["dt"] +                    # Derive and format date
                                                api_data["timezone_offset"] -
                                                SYSTEM_TIME_UTC_OFFSET).strftime("%a %e %B %Y")

            print_sunrise = datetime.fromtimestamp(api_data["daily"][i]["sunrise"] +    # Derive and format sunrise time
                                                   api_data["timezone_offset"] -
                                                   SYSTEM_TIME_UTC_OFFSET).strftime("%H:%M")

            print_sunset = datetime.fromtimestamp(api_data["daily"][i]["sunset"] +       # Derive and format sunset time
                                                  api_data["timezone_offset"] -
                                                  SYSTEM_TIME_UTC_OFFSET).strftime("%H:%M")
            f.write(f'{print_date}, Sunrise: {print_sunrise}, Sunset: {print_sunset}\n')

            f.write(f'    Prevailing conditions:    '
                    f'{api_data["daily"][i]["weather"][0]["description"]}, ')            # Prevailing weather conditions

            wind_speed = round(api_data["daily"][i]["wind_speed"] / 1000 * 3600)    # Convert wind speed from mps to kph
            f.write(f'wind speed: '                                                                  # Output wind speed
                    f'{wind_speed:}kph\n')

            f.write(f'    Temperatures:             '                          # Output maximum and minimum temperatures
                    f'Max {round(api_data["daily"][i]["temp"]["max"]): >3}°C,    '                 # Maximum temperature
                    f'Min {round(api_data["daily"][i]["temp"]["min"]): >3}°C\n')                   # Minimum temperature

            f.write(f'    day/night/evening/morning '              # Output day, night, evening and morning temperatures
                    f'{round(api_data["daily"][i]["temp"]["day"]): >3}°C,  '                           # Day temperature
                    f'{round(api_data["daily"][i]["temp"]["night"]): >3}°C,  '                       # Night temperature
                    f'{round(api_data["daily"][i]["temp"]["eve"]): >3}°C,  '                       # Evening temperature
                    f'{round(api_data["daily"][i]["temp"]["morn"]): >3}°C\n')                      # Morning temperature

            f.write(f'    Feels like                '       # Output day, night, evening and morning "feels like" temps.
                    f'{round(api_data["daily"][i]["feels_like"]["day"]): >3}°C,  '        # "Feels like" day temperature
                    f'{round(api_data["daily"][i]["feels_like"]["night"]): >3}°C,  '    # "Feels like" night temperature
                    f'{round(api_data["daily"][i]["feels_like"]["eve"]): >3}°C,  '    # "Feels like" evening temperature
                    f'{round(api_data["daily"][i]["feels_like"]["morn"]): >3}°C\n')   # "Feels like" morning temperature

            f.write("\n")                                                                    # New line to leave a space

# We have processed both hourly and daily reports for each location, ergo we have done our job.  Let's tell the world
print()                                                                                     # Blank line before good-bye
print("***** Weather Forecast program has finished *****")                       # Tell the world we've finished our job
print()

# Tell the world how long it took
finish_time = time.time()
elapsed_time = finish_time - start_time
print("Elapsed time: ", time.strftime("%H:%M:%S", time.gmtime(elapsed_time)))

# Close the terminal window
x = input("Press ENTER to close the terminal window ")          # Keep the terminal window open until the user closes it
