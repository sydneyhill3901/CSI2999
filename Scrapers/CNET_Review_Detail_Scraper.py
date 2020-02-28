import csv
import requests
from bs4 import BeautifulSoup
import time


phoneList = []
scoreBreakdownList = []
phoneGoodBadBottomLineList = []


def CreateScoreBreakdownCSV():
    with open('CNET_ScoreBreakdown.csv', 'wt', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for i in scoreBreakdownList:
            phone = i[0]
            header = i[1]
            rating = i[2]
            filewriter.writerow([phone, header, rating])


def CreateGoodBadCSV():
    with open('CNET_Good_Bad_BottomLine.csv', 'wt', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for i in phoneGoodBadBottomLineList:
            phone = i[0]
            description = i[1]
            sentiment = i[2]
            filewriter.writerow([phone, description, sentiment])


def search_theGood(phone_name, websource):
    phonereview = websource.find("p", {"class": "theGood"})
    phoneGoodBadBottomLineList.append([phone_name, phonereview.span.text, "Good"])


def search_theBad(phone_name, websource):
    phonereview = websource.find("p", {"class": "theBad"})
    phoneGoodBadBottomLineList.append([phone_name, phonereview.span.text, "Bad"])


def search_theBottomLine(phone_name, websource):
    phonereview = websource.find("p", {"class": "theBottomLine"})
    phoneGoodBadBottomLineList.append([phone_name, phonereview.span.text, "Bottom Line"])


def search_goodreviews(phone_name, websource):
    phonereview = websource.find_all("div", {"class": "c-reviewCard_chunk"})
    phonereviewslist = []
    phonereviewsentimentlist = []
    for i in range(len(phonereview)):
        if "Like" in phonereview[i].text:
            phone_statements = phonereview[i].find_all("span", {"class": "c-reviewCard_listText"})
            for statements in phone_statements:
                phonereviewslist.append(statements.text)
                phonereviewsentimentlist.append(phonereview[i].h3.text)
    for i in range(len(phonereviewslist)):
        phoneGoodBadBottomLineList.append([phone_name, phonereviewslist[i], phonereviewsentimentlist[i]])


def search_scorebreakdown_page_type_2(phone_name, websource):
    scoreheaders = websource.find_all("div", {"class": "categoryWrap"})
    scoreheaderslist = []
    scoreratingslist = []
    for headers in scoreheaders:
        scoreheaderslist.append(headers.span.text)
        scoreratingslist.append(headers.strong.text)
    for i in range(len(scoreheaderslist)):
        scoreBreakdownList.append([phone_name, scoreheaderslist[i], scoreratingslist[i]])


def search_scorebreakdown(phone_name, websource):
    scoreheaders = websource.find_all("span", {"class": "c-reviewPostcap_rateTitle"})
    scoreheaderslist = []
    for headers in scoreheaders:
        scoreheaderslist.append(headers.text)
    scoreratings = websource.find_all("span", {"class": "c-reviewPostcap_rating"})
    scoreratinglist = []
    for ratings in scoreratings:
        scoreratinglist.append(ratings.text)
    for i in range(len(scoreratinglist)):
        scoreBreakdownList.append([phone_name, scoreheaderslist[i], scoreratinglist[i]])


# Requests the page and sends the html back to the main function
def get_webpage(url):
    try:
        req = requests.get(url)
        soup = BeautifulSoup(req.text, features="lxml")
        return soup
    except Exception as e:
        print(f"Error: \n{e}")


# https://docs.python.org/2/library/csv.html
def read_csv():
    with open("CNET_Phone_Ratings_Url.csv", "rt") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        for row in reader:
            phoneList.append(row)  # Adding the csv to a list to search each page


def main():
    read_csv()  # Start main by reading the csv and putting items into a list
    for phones in range(18):
        page_text = get_webpage(phoneList[phones][1])  # Gets the page text to grab the info from
        if page_text.find_all("span", {"class": "c-reviewPostcap_rateTitle"}):
            search_scorebreakdown(phoneList[phones][0], page_text)
        elif page_text.find_all("div", {"class": "categoryWrap"}):
            search_scorebreakdown_page_type_2(phoneList[phones][0], page_text)
        if page_text.find_all("div", {"class": "c-reviewCard_chunk"}):
            search_goodreviews(phoneList[phones][0], page_text)
        elif page_text.find_all("p", {"class": "theGood"}):
            search_theGood(phoneList[phones][0], page_text)
            search_theBad(phoneList[phones][0], page_text)
            search_theBottomLine(phoneList[phones][0], page_text)
        time.sleep(10)
    CreateScoreBreakdownCSV()
    CreateGoodBadCSV()
    # print(scoreBreakdownList)
    print(phoneGoodBadBottomLineList)


# Start with the main function of the code
main()
