import requests            # make the api request
import json                # parse the data
import pandas as pd        # graph the data
import time                # delay
import os                  # open local file
from datetime import datetime  # compare how long its been

# Apply for first time Texas CLP/CDL -          TypeId = 71
# Change, replace or renew Texas DL/Permit -    TypeId = 81
# Class C Road Skills Test -                    TypeId = 21
TypeId = 71       # ^^^
ZipCode = 76036   # How far from here
dtRatio = 1.5     # Time/Distance ratio | days per mile


def request(TypeId=TypeId, ZipCode=ZipCode):
    """Requests from the DMV api.
    Takes in the TypeId and ZipCode.
    Returns a list of all locations
    that are availible right now.
    """
    locations = requests.post(
        url="https://publicapi.txdpsscheduler.com/api/AvailableLocation",
        data=json.dumps({"TypeId": TypeId,
                         "ZipCode": f"{ZipCode}",
                         "CityName": "",
                         "PreferredDay": 0}),
        headers={"Origin": "https://public.txdpsscheduler.com"})
    return json.loads(locations.content.decode("utf-8"))


def parse(locations: list, dtRatio=dtRatio):
    """Parses the reqest.
    Takes in the locations and dtRatio.
    Returns the lists: name,
    distance, date, days, and score.
    """
    name, distance, date, days, score = [], [], [], [], []
    for location in locations:
        name.    append(location["Name"])
        distance.append(location["Distance"])
        date.    append(location["NextAvailableDate"])
        delta = datetime(int(location["NextAvailableDateYear"]),
                         int(location["NextAvailableDateMonth"]),
                         int(location["NextAvailableDateDay"])
                         ) - datetime.now()
        days.    append(delta.days)
        score.   append(int(100 -
                        (delta.days + dtRatio*int(location["Distance"]))))
    return name, distance, date, days, score


def graph(name: list, distance: list, date: list, days: list, score: list):
    """Graphs the locations on pandas.
    Takes in the name, distance, date, and score.
    Returns the sorted pandas dataframe.
    """
    data = {"Name": name, "Distance": distance, "Date": date,
            "Days": days, "Score": score}
    dataframe = pd.DataFrame(data)
    dataframe = dataframe.sort_values(by=["Score"], ascending=False)
    return dataframe


def update(counter, current_score):
    """Calls and checks for changes.
    Takes in the counter and current_score.
    Prints if there has been a change and
    returns the latest score list.
    """
    name, distance, date, days, score = parse(request(), dtRatio)
    if current_score == score:
        print(f"#{str(counter).zfill(6)} | SAME :( | Best Score: {max(score)}",
              end="\r")
        counter += 1
        return counter, score
    else:
        print("\n", graph(name, distance, date, days, score))
        os.system('''
        "C:/Program Files (x86)/K-Lite Codec Pack/MPC-HC64/mpc-hc64.exe"\
         sms-alert-4-daniel_simon.mp3 /play /close /minimized''')
        return counter, score


if __name__ == "__main__":
    counter = 0
    current_score = []
    while True:
        counter, current_score = update(counter, current_score)
        time.sleep(1)
