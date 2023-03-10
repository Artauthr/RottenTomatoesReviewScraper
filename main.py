import requests
from bs4 import BeautifulSoup as bs 
import pandas as pd

df = pd.DataFrame(columns=["username","link","review"])

url = "https://www.rottentomatoes.com/tv/daisy_jones_and_the_six/s01/reviews?type=user"  # <----- Put user reviews page of the show here.

final_url_start = "https://www.rottentomatoes.com/napi/seasonReviews/"
headers = {"user-agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36"}
result = requests.get(url=url, headers=headers)

content = result.text
soup = bs(content,"html.parser")

code = soup.find("script",{"id":"mps-page-integration"}).text
idcode = code[code.find("field[emsId]")+15:code.find(";")-2]

initialRequest = final_url_start + idcode + "?type=user"
initialResult = requests.get(url=initialRequest, headers=headers).json()

jsonResults = [initialResult]

while True:
    if initialResult["pageInfo"]["hasNextPage"]:
        try:
            endCursor = initialResult["pageInfo"]["endCursor"]
            startCursor = initialResult["pageInfo"]["startCursor"]
        except:
            endCursor = initialResult["pageInfo"]["endCursor"]
            startCursor = ""

        nextRequest = initialRequest + "&f=null&direction=next&endCursor=" + endCursor + "&startCursor=" + startCursor 
        nextResult = requests.get(url=nextRequest, headers=headers).json()
        jsonResults.append(nextResult)  
        initialResult = nextResult
    else:
        break

for result in jsonResults:
    for i in range(len(result["reviews"])):
        quote = result["reviews"][i]["review"]
        name = result["reviews"][i]["user"]["displayName"]
        url = result["reviews"][i]["user"]["accountLink"] 
        fullUrl = "https://www.rottentomatoes.com/" + url
        df = df.append(pd.Series([name, fullUrl, quote], index = df.columns), ignore_index=True)


df.to_csv("TomatoReviews.csv", encoding='utf-8')