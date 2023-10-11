import requests
import os
import json
import re
import zipfile

# ENVIRONMENT DETAILS
TOKEN = ''
DATE = '10/03/2023'
# BASE_URL = 'https://api-dev.headspin.io'
BASE_URL = 'https://ericssonmana-api.ran.rc.us.am.ericsson.se'

# Function to dynamically fetch keys for the Time Series Session Data
def fetchKeys(SESSION):
    print(f"Downloading TIME SERIES KEYS for {SESSION['session_id']}")
    KEY_API = f"{BASE_URL}/v0/sessions/timeseries/{SESSION['session_id']}/info"
    response = requests.get(KEY_API, headers={'Authorization': 'Bearer {}'.format(TOKEN)})
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Failed to fetch KEY info. {response.status_code} : {response.text}")
        return "DOWNLOAD FAILED"
    
# Function to use the keys to dynamically gather all the Time Series Data.
def fetchInfo(KEY,SESSION):
    INFO_API = f"{BASE_URL}/v0/sessions/timeseries/{SESSION['session_id']}/download?key="
    response = requests.get(INFO_API + KEY, headers={'Authorization': 'Bearer {}'.format(TOKEN)})

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch TIME SERIES info. {response.status_code} : {response.text}")
        return "DOWNLOAD FAILED"

    
# Function to fetch and then export to JSON format all issues
def fetchIssues(SESSION):
    print(f"Downloading ISSUES for {SESSION['session_id']}")
    # ISSUE_API = f"{BASE_URL}/v0/sessions/analysis/issues/{SESSION['session_id']}?orient=record"
    ISSUE_API = f"{BASE_URL}/v0/sessions/analysis/issues/{SESSION['session_id']}"

    response = requests.get(ISSUE_API, headers={'Authorization': 'Bearer {}'.format(TOKEN)})
    if response.status_code == 200:
        DATA = json.loads(response.text)
        for ENTRY in DATA:    
            if "Issue Start" in DATA[ENTRY].keys():
                timeData = []
                for i in range(len(DATA[ENTRY]['Issue Start'])):
                    timing = {}
                    timing['startTime'] = DATA[ENTRY]['Issue Start'][i]
                    if "Issue End" in DATA[ENTRY]:
                        timing['endTime'] = DATA[ENTRY]['Issue End'][i]
                    timeData.append(timing)
                for time in timeData:
                    startTime = re.split(r'[:.]', time['startTime'])
                    startTime = int(startTime[0])*(3600*1000) + int(startTime[1])*(60*1000) + int(startTime[2])*(1000) + int(startTime[3])
                    DATA[ENTRY]['Issue Start'] = startTime
                    if "Issue End" in DATA[ENTRY]:
                        endTime = re.split(r'[:.]', time['endTime'])
                        endTime = int(endTime[0])*(3600*1000) + int(endTime[1])*(60*1000) + int(endTime[2])*(1000) + int(endTime[3])
                        DATA[ENTRY]['Issue End'] = endTime

        exportJSON(DATA)
        return
    else:
        print("Failed to fetch session info.")
        return "DOWNLOAD FAILED"

            # for KEY in DATA:
            #     for i in range(len(DATA[KEY])):
                   
            #        SESSION['start_time']
            #     #    str(float(ENTRY[1])/1000 + SESSION['start_time'])
            #        [DATA[KEY][i]['Issue Start'], DATA[KEY][i]['Issue End']] = ["a",'b']
            #        print(i)

                    

    



def exportToCSV(DATA,FILE):
    PATH = os.path.join(os.getcwd(), SESSION['session_id'])
    if not os.path.exists(PATH):
        os.makedirs(SESSION['session_id'])
    try:
        with open(f"{PATH}/{SESSION['session_id']}_{FILE}", 'w', newline='') as csvfile:
            for line in DATA:
                csvfile.write(line + "\n")
    except Exception as e:
        print(f'Error exporting data to {FILE}: {str(e)}')


def fetchTimeSeriesData(SESSION):
    KEYS = fetchKeys(SESSION)
    print(f"Downloading TIME SERIES DATA for {SESSION['session_id']}")
    for KEY in KEYS:
        i=0
        DATA = fetchInfo(KEY,SESSION)
        DATA = DATA.split("\n")
        for ENTRY in DATA:
            ENTRY = ENTRY.split(',')
            if ENTRY != [''] and ENTRY[1] != 'Time' and ENTRY[1] != '0.0':
                try:
                    ENTRY[1] = str(float(ENTRY[1])/1000 + SESSION['start_time'])
                except Exception as e:
                    print(e)
            ENTRY = ",".join(ENTRY)
            DATA[i]=ENTRY
            i+=1
        try:
            exportToCSV(DATA,KEY + ".csv")
        except Exception as e:
            print(e)
    return

def exportJSON(DATA):
    PATH = os.path.join(os.getcwd(), SESSION['session_id'])
    if not os.path.exists(PATH):
        os.makedirs(SESSION['session_id'])
    try:
        with open(f"{PATH}/{SESSION['session_id']}_Issues.json", "w") as jsonfile:
            json.dump(DATA,jsonfile)
    except Exception as e:
            print(f"Error in exportJSON function: {e}")


# Function to collect NUM ammount of sessions (defined at the top)
def collectSessions(DATE):
    print(f"Collecting Sessions for {DATE}")
    SESSIONS_API = f'{BASE_URL}/v0/sessions?include_all=true&tag=Date:{DATE}&num_sessions=100'

    try:
        response = requests.get(SESSIONS_API, headers={'Authorization': 'Bearer {}'.format(TOKEN)})
        SESSIONS = json.loads(response.text)['sessions']
        for SESSION in SESSIONS:
            if(SESSION['state'] != 'ended'):
                SESSION.pop()
        return SESSIONS
    except Exception as e:
        print(f"Error in collectSessions function: {e}")
        return []



# PROGRAM MAIN
if __name__ == "__main__":
    SESSIONS = collectSessions(DATE)
    for SESSION in SESSIONS:
        try:
            fetchTimeSeriesData(SESSION)
            fetchIssues(SESSION)
        except Exception as e:
            print(f"Error with Session: {SESSION['session_id']}: {e}")






















# Function to fetch & export HAR File
# WIP NOT FINISHED
def fetchHAR(SESSION):
    print(f"Downloading HAR data for {SESSION['session_id']}")
    DATA_API = f"{BASE_URL}/v0/sessions/{SESSION}."
    response = requests.get(DATA_API + "har?enhanced=True", headers={'Authorization': 'Bearer {}'.format(TOKEN)})
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch HAR data. {response.status_code} : {response.text}")
        return "DOWNLOAD FAILED"

# Function to fetch & export PCAP File
# WIP NOT FINISHED
def fetchPCAP(SESSION):
    print(f"Downloading PCAP data for {SESSION['session_id']}")
    DATA_API = f"{BASE_URL}/v0/sessions/{SESSION}."
    response = requests.get(DATA_API + "pcap", headers={'Authorization': 'Bearer {}'.format(TOKEN)})
    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to fetch PCAP data. {response.status_code} : {response.text}")
        return "DOWNLOAD FAILED"


