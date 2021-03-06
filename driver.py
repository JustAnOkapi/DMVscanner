import requests
import pandas as pd
import json
import time
import os


url = 'https://publicapi.txdpsscheduler.com/api/AvailableLocation'
payload = {
  "TypeId": 71,
  "ZipCode": "76036",
  "CityName": "",
  "PreferredDay": 0
}
headers = {
"Accept": "application/json, text/plain, */*",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-US,en;q=0.9",
"Connection": "keep-alive",
"Content-Length": "62",
"Content-Type": "application/json;charset=UTF-8",
"DNT": "1",
"Host": "publicapi.txdpsscheduler.com",
"Origin": "https://public.txdpsscheduler.com",
"Referer": "https://public.txdpsscheduler.com/",
"Sec-Fetch-Dest": "empty",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-site",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36 OPR/71.0.3770.234"
}
Global_Scores = []

def search(Global_Scores_inp):
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    list_data = json.loads( r.content.decode("utf-8") )

# for data in list_data:
#     print(data)

    Name = []
    Distance = []
    Date = []
    Scores = []

    for location in list_data:
        Score = 50
        if location["NextAvailableDateYear"] == '2020':
            Score -= int( float(location['NextAvailableDateMonth']) * 2 - 20 )
            Score -= int( float(location['NextAvailableDateDay']) * 6.6 / 100 )
        elif location["NextAvailableDateYear"] == '2021':
            Score -= int( float(location['NextAvailableDateMonth']) * 2 + 5 )
            Score -= int( float(location['NextAvailableDateDay']) * 6 / 100 )
        Score -= int(location["Distance"])
        
        Scores.append(   Score)
        Name.append(     location["Name"])
        Distance.append( int(location["Distance"]))
        Date.append(     location["NextAvailableDate"])

    data = {'Name': Name,'Distance': Distance, "Date": Date, "Score": Scores}
    df = pd.DataFrame(data)
    df = df.sort_values(by=["Score"], ascending=False)

    if Scores != Global_Scores_inp:
        print("\n")
        print(df)
        print("\n")
        os.system('"C:/Program Files (x86)/K-Lite Codec Pack/MPC-HC64/mpc-hc64.exe" sms-alert-4-daniel_simon.mp3 /play /close /minimized')
        Global_Scores_out = Scores
        return Global_Scores_out
    elif Scores == Global_Scores_inp:
        if counter % 10 == 0:
            print(f"#{str(int(counter/10)).zfill(5)} | SAME :( | Best Score: {df.iloc[0, 3]}", end='\r')


counter = 0

while True: 
    counter += 1
    Global_Scores_new = search(Global_Scores)
    if Global_Scores_new == None:
        Global_Scores_new = Global_Scores
    if Global_Scores_new != Global_Scores:
        Global_Scores = Global_Scores_new
    time.sleep(1)
