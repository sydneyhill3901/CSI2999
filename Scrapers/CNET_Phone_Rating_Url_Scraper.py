import requests
import csv
from bs4 import BeautifulSoup
import time
from datetime import datetime


def Main():
    PrintTime("Start Time: ")

    # Step 1 Get Last Page Number
    lastPage = GetLastPage()
    time.sleep(10)

    # Step 2 Fill Phone List(List Layout : "Name", "Url", "Rating")
    FillPhoneList(lastPage)

    # Step 3 Convert Ratings
    ConvertRatings()

    # Step 4 Create CSV File
    CreateCSVFile()

    PrintTime("End Time: ")

# Print the time so I know how long the project runs for
# Source: https://stackoverflow.com/questions/16138744/extract-time-from-datetime
# -and-determine-if-time-not-date-falls-within-range
def PrintTime(timeNotifier):
    timeNow = datetime.now()
    currentTime = timeNow.strftime("%H:%M")
    print(timeNotifier + currentTime)

# Get the last page of the site so I know how many pages I need to search
# Source Used: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
def GetLastPage():
    try:
        req = requests.get('https://www.cnet.com/topics/phones/products/')
        soup = BeautifulSoup(req.text, features="lxml")
        lastPageNumber = soup.find("a", {"class": "page last"}).text
        return lastPageNumber
    except Exception as e:
        print(f"Error\n{e}")

#  the phone list going page by page finding the sections and grabbing the information that is needed
# Source Used: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
def FillPhoneList(lastPage):
    try:
        pageNumber = 1
        for pageNumber in range(int(lastPage) + 1):# replace 3 with lastPage to grab all the pages
            # This if only runs once when it is the first page
            if(pageNumber == 1):
                req = requests.get('https://www.cnet.com/topics/phones/products/')
                soup = BeautifulSoup(req.text, features="lxml")
                phonesInfo = soup.find_all("section", {"class" : ["col-3 searchItem product", "col-3 searchItem product left"]})
                for phoneInfo in phonesInfo:
                    phoneName = phoneInfo.h3
                    phoneUrl = phoneInfo.a['href']
                    phoneRating = phoneInfo.meta['content']

                    if ("reviews" in phoneUrl):
                        PhonesUrlRatingList.append((phoneName.text.strip().replace("\n",""),
                                                    "https://www.cnet.com"+phoneUrl, float(phoneRating)))
                time.sleep(10)
            # For pages after the first page
            else:
                req = requests.get('https://www.cnet.com/topics/phones/products/'+str(pageNumber))
                soup = BeautifulSoup(req.text, features="lxml")
                phonesInfo = soup.find_all("section",
                                           {"class": ["col-3 searchItem product", "col-3 searchItem product left"]})
                for phoneInfo in phonesInfo:
                    phoneName = phoneInfo.h3
                    phoneUrl = phoneInfo.a['href']
                    try:
                        phoneRating = phoneInfo.meta['content']
                    except Exception as ex:
                        phoneRating=0
                    # if(phoneInfo.meta['content'] is None):
                    #     phoneRating = 0
                    # else:
                    #     phoneRating = phoneInfo.meta['content']
                    if ("reviews" in phoneUrl):
                        PhonesUrlRatingList.append((phoneName.text.strip().replace("\n", ""),
                                                    "https://www.cnet.com" + phoneUrl, float(phoneRating)))
                time.sleep(10)
    except Exception as e:
        print(f"Error\n{e}\n{pageNumber}")

#  the ratings in the original list to a max of 10 and put into a new list
def ConvertRatings():
    for i in PhonesUrlRatingList:
        phoneName = i[0]
        phoneName = ' '.join(phoneName.split())
        rating = i[2]
        rating = (rating/5)*10
        if(rating == 0):
            rating = 'N/A'
        RevisedRatingList.append((phoneName,i[1],rating))


# take the created list and make a csv file
# Source: https://pythonspot.com/files-spreadsheets-csv/
def CreateCSVFile():
    with open('CNET_Phone_Ratings_Url.csv', 'wt', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for i in RevisedRatingList:
            phone = i[0]
            url = i[1]
            rating = i[2]
            filewriter.writerow([phone, url, rating])


PhonesUrlRatingList = []
RevisedRatingList = []
Main()