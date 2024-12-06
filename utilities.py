import requests
import gzip
import io
import xml.etree.ElementTree as ET
import csv
import pandas
from time import sleep
import datetime
from tzlocal import get_localzone

tags = ["NAME","UNSTATUS","ENDORSEMENTS","REGION","LASTLOGIN","INFLUENCENUM"]

def last_activity(lastlogin:int,lastmajor:datetime.datetime) -> float:
    """Calculate the the time since last login in days. Lastlogin should be a unix timestamp.
    Returns a float."""
    timediff = lastmajor - datetime.datetime.fromtimestamp(lastlogin,tz=datetime.timezone.utc)
    return round(timediff.total_seconds()/86400,2)

def endocounter(endos) -> int:
    """count the number of endos a nation has"""
    if isinstance(endos, float):
        #Only the NaNs should come up as floats when checked
        return 0
    else:
        return len(endos.split(","))
    
def efficiency(endos:int,influence:int,last_login:float) -> float:
    """Attempts to weight how much future influence is saved by banning a nation now against its cost"""
    if last_login > 8:
        #the nation is inactive and not gaining influence
        return 0
    elif influence == 0:
        #If inf is 0 they are free to ban. They therefore technically have infinite value, but dividing by 0 breaks math so we hardcode
        return 9999999
    else:
        return (endos + 1)/influence
    
def url_maker(nation:str) -> str:
    """url maker"""
    return "https://www.nationstates.net/nation={}".format(nation)

def get_data_dump(user:str):
    """Downloads the Data Dump and saves a csv file for future use"""
    print("Making a Request to the Server")
    try:
        headers = {'User-Agent':'{} Using Mathinator3 by DragoE'.format(user)}
        response = requests.get("https://www.nationstates.net/pages/nations.xml.gz", headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(e)
        return None
    
    print("Got a good response. Unzipping")
    file = io.BytesIO(response.content)
    with gzip.GzipFile(fileobj=file) as f:
        xml_content = f.read()
    
    tree = ET.fromstring(xml_content)
    print("Parsing Tree")
    data = []
    for nation in tree.findall("NATION"):
        row = []
        for tag in tags:
            element = nation.find(tag)
            row.append(element.text)
        data.append(row)
    #List comprehension to make the names properly formatted
    data = [[x[0].lower().replace(" ","_"), *x[1:3], x[3].lower().replace(" ","_"), *x[4:]] for x in data]
        
    print("Done. Saving Result")
    with open("nations.csv", mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(tags)
        writer.writerows(data)
    print("File saved.")
    
def make_regiontable(nations:pandas.DataFrame, region:str, user:str):
    """Takes in a DataFrame containing the daily dump info, and a region name.
    Assumes region name is aready formatted
   Produces and saves a new csv table for a given region"""
    #Get the most up-to-date list of nations in the region
    try:
        headers = {'User-Agent':'{} Using Mathinator3 by DragoE'.format(user)}
        response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?region={}&q=nations".format(region), headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(e)
        return None
    sleep(0.7) #Rate Limit Saftey
    tree = ET.fromstring(response.text)
    region_nations = tree.find("NATIONS").text.split(":")
    #Set up our new dataframe
    regiontable = pandas.DataFrame(columns=tags)
    
    #Figure out how long its been since the last major
    EST = datetime.timezone(datetime.timedelta(hours=-5))
    local_tz = get_localzone()
    now = datetime.datetime.now(tz=local_tz)
    now_est = now.astimezone(EST)
    last_major = now_est.replace(hour=0,minute=0)
    
    for nation in region_nations:
        #find the index of that nation
        nationdata = nations.loc[nations["NAME"] == nation]
        if nationdata.empty:
            #It doesn't exist in the dump. Create a placeholder DF for it until we get more info later.
            nationdata = pandas.DataFrame([[nation,"a","_","c","d","e"]],columns=tags)
        print(nationdata.iloc[0]["NAME"])
        if nationdata.iloc[0]["REGION"] == region:
            if (now - last_major) < datetime.timedelta(hours=12):
                #If it's been less then 12h since major, minor hasn't happened yet, and we can take dump info at face value
                regiontable = pandas.concat([regiontable,nationdata],ignore_index=True)
            else:
                #If minor has happened, we will approximate that gain from endorsements. This can overestimate but is easier then pining the API 500 times
                if (last_major - datetime.datetime.fromtimestamp(nationdata.iloc[0]["LASTLOGIN"], tz=datetime.timezone.utc)) < datetime.timedelta(days=8):
                    if isinstance(nationdata.iloc[0]["ENDORSEMENTS"], float):
                        #Only the NaNs should come up as floats when checked
                        nationdata.replace(nationdata.iloc[0]["INFLUENCENUM"], nationdata.iloc[0]["INFLUENCENUM"] + 1, inplace=True)
                    else:
                         nationdata.replace(nationdata.iloc[0]["INFLUENCENUM"], nationdata.iloc[0]["INFLUENCENUM"] + (len((nationdata.iloc[0]["ENDORSEMENTS"]).split(",")) + 1), inplace=True)
                    regiontable = pandas.concat([regiontable,nationdata],ignore_index=True)
                else:
                    regiontable = pandas.concat([regiontable,nationdata],ignore_index=True)              
        else:
            #Nation is a recent move. Check it further using the API
            try:
                response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=wa".format(nation), headers=headers)
                response.raise_for_status()
                tree = ET.fromstring(response.text)
                nationdata.replace(nationdata.iloc[0]["UNSTATUS"], tree.find("UNSTATUS").text, inplace=True)
            except Exception as e:
                print(e)
            sleep(0.7)
            try:
                response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=endorsements".format(nation), headers=headers)
                response.raise_for_status()
                tree = ET.fromstring(response.text)
                nationdata.replace(nationdata.iloc[0]["ENDORSEMENTS"], tree.find("ENDORSEMENTS").text, inplace=True)
            except Exception as e:
                print(e)
            sleep(0.7)
            try:
                response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=lastlogin".format(nation), headers=headers)
                response.raise_for_status()
                tree = ET.fromstring(response.text)
                nationdata.replace(nationdata.iloc[0]["LASTLOGIN"], tree.find("LASTLOGIN").text, inplace=True)
            except Exception as e:
                print(e)
            sleep(0.7)
            try:
                response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=influencenum".format(nation), headers=headers)
                response.raise_for_status()
                tree = ET.fromstring(response.text)
                nationdata.replace(nationdata.iloc[0]["INFLUENCENUM"], tree.find("INFLUENCENUM").text, inplace=True)
            except Exception as e:
                print(e)
            sleep(0.7)
    
    regiontable["ENDORSEMENTS"] = regiontable["ENDORSEMENTS"].apply(lambda x: endocounter(x))
    regiontable["LASTLOGIN"] = regiontable["LASTLOGIN"].apply(lambda x: last_activity(x,last_major))  
    regiontable["URL"] = regiontable["NAME"].apply(lambda x: url_maker(x))
    (regiontable.drop(columns='REGION')).to_csv("regiontable.csv",index=False,header=True)
    print("Done")
    
def officer_check(user:str,region:str,regiontable:pandas.DataFrame) -> pandas.DataFrame:
    """Gets a DataFrame of just the ROs from the larger regiontable. Assumes inputs properly formatted"""
    #Get the list of ROs
    try:
        headers = {'User-Agent':'{} Using Mathinator3 by DragoE'.format(user)}
        response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?region={}&q=officers".format(region), headers=headers)
        response.raise_for_status()
        tree = ET.fromstring(response.text)
        officer_elements = tree.find("OFFICERS").findall("OFFICER")
        ROs = []
        for element in officer_elements:
            ROs.append(element.find("NATION").text)
    except Exception as e:
        print(e)
        return None
    sleep(0.7)
    #Get the delegate and make sure its included
    try:
        response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?region={}&q=delegate".format(region), headers=headers)
        response.raise_for_status()
        tree = ET.fromstring(response.text)
        wad = tree.find("DELEGATE").text
    except Exception as e:
        print(e)
        return None
    sleep(0.7)
    if wad not in ROs:
        ROs.append(wad)
        
    #Now search the table for the ROs
    ro_table = regiontable[(regiontable["NAME"].isin(ROs))]
    return ro_table

def delendos(user:str,region:str) -> tuple[list[str],str]:
    try:
        headers = {'User-Agent':'{} Using Mathinator3 by DragoE'.format(user)}
        response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?region={}&q=delegate".format(region), headers=headers)
        response.raise_for_status()
        tree = ET.fromstring(response.text)
        wad = tree.find("DELEGATE").text
    except Exception as e:
        print(e)
        return None
    sleep(0.7)
    try:
        response = requests.get("https://www.nationstates.net/cgi-bin/api.cgi?nation={}&q=endorsements".format(wad), headers=headers)
        response.raise_for_status()
        tree = ET.fromstring(response.text)
        sleep(0.7)
        return tree.find("ENDORSEMENTS").text.split(",")
    except Exception as e:
        print(e)
        return None
     
    
if __name__ == "__main__":
    print("e")
    