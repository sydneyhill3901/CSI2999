import csv
import requests
from bs4 import BeautifulSoup
import time
import sqlite3


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
    GoodReview = ""
    BadReview = ""
    for i in range(len(phonereview)):
        if "Like" in phonereview[i].text:
            phone_statements = phonereview[i].find_all("span", {"class": "c-reviewCard_listText"})
            for statements in phone_statements:
                phonereviewslist.append(statements.text)
                phonereviewsentimentlist.append(phonereview[i].h3.text)
    for i in range(len(phonereviewslist)):
        if phonereviewsentimentlist[i] == "Don't Like":
            BadReview = BadReview + "\n" + phonereviewslist[i]
        else:
            GoodReview = GoodReview + "\n" + phonereviewslist[i]
    phoneGoodBadBottomLineList.append([phone_name, GoodReview.strip(), "Like"])
    phoneGoodBadBottomLineList.append([phone_name, BadReview.strip(), "Don't Like"])


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


# Source: https://docs.python.org/3/library/sqlite3.html
def PlaceScoresInDatabase(phone, header, rating, conn, c):
    c.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (phone.replace("+", " plus").replace("(", "").replace(")", " ").strip().lower(),))
    phoneid = c.fetchone()[0]
    c.execute("SELECT count(*) FROM CellCheck_CNETDetailedScore WHERE Phone_id = ?", (phoneid,))
    exists = c.fetchone()[0]
    if exists == 0:
        c.execute("INSERT INTO CellCheck_CNETDetailedScore (Phone_id, Design, Features, Performance, Camera, Battery)"
                  " values (?, ?, ?, ?, ?, ?)",
                  (phoneid, rating, "", "", "", ""))
        conn.commit()
    elif header == "Design":
        c.execute("UPDATE CellCheck_CNETDetailedScore SET Design = ? WHERE Phone_id = ?", (rating, phoneid,))
        conn.commit()
    elif header == "Features":
        c.execute("UPDATE CellCheck_CNETDetailedScore SET Features = ? WHERE Phone_id = ?", (rating, phoneid,))
        conn.commit()
    elif header == "Performance":
        c.execute("UPDATE CellCheck_CNETDetailedScore SET Performance = ? WHERE Phone_id = ?", (rating, phoneid,))
        conn.commit()
    elif header == "Camera":
        c.execute("UPDATE CellCheck_CNETDetailedScore SET Camera = ? WHERE Phone_id = ?", (rating, phoneid,))
        conn.commit()
    elif header == "Battery":
        c.execute("UPDATE CellCheck_CNETDetailedScore SET Battery = ? WHERE Phone_id = ?", (rating, phoneid,))
        conn.commit()


# Source: https://docs.python.org/3/library/sqlite3.html
def UpdateProDatabase(phone, description, conn, c):
    c.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (phone.replace("+", " plus").replace("(", "").replace(")", " ").strip().lower(),))
    phoneid = c.fetchone()[0]
    c.execute("SELECT * FROM CellCheck_Site WHERE SiteName = 'CNET'")
    siteid = c.fetchone()[0]
    c.execute("SELECT count(*) FROM CellCheck_ProList WHERE Phone_id = ? AND Site_id = ?",
              (phoneid, siteid))
    exists = c.fetchone()[0]
    if exists == 0:
        c.execute("INSERT INTO CellCheck_ProList (Phone_id, Site_id, Pros)"
                  " values (?, ?, ?)",
                  (phoneid, siteid, description.strip()))
        conn.commit()


# Source: https://docs.python.org/3/library/sqlite3.html
def UpdateConDatabase(phone, description, conn, c):
    c.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (phone.replace("+", " plus").replace("(", "").replace(")", " ").strip().lower(),))
    phoneid = c.fetchone()[0]
    c.execute("SELECT * FROM CellCheck_Site WHERE SiteName = 'CNET'")
    siteid = c.fetchone()[0]
    c.execute("SELECT count(*) FROM CellCheck_ConList WHERE Phone_id = ? AND Site_id = ?",
              (phoneid, siteid))
    exists = c.fetchone()[0]
    if exists == 0:
        c.execute("INSERT INTO CellCheck_ConList (Phone_id, Site_id, Cons)"
                  " values (?, ?, ?)",
                  (phoneid, siteid, description.strip()))
        conn.commit()


def main():
    read_csv()  # Start main by reading the csv and putting items into a list
    for phones in range(18):
        try:
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
        except Exception as e:
            print(f"Error syncing to Database \n{e}")
        time.sleep(10)
    CreateScoreBreakdownCSV()
    CreateGoodBadCSV()
    # print(scoreBreakdownList)
    # print(phoneGoodBadBottomLineList)

    # # Add info into database
    # conn = sqlite3.connect(r'C:\Users\Andrew\Documents\CSI2999\CSI2999\CSI2999\db.sqlite3')
    conn = sqlite3.connect("../CSI2999/db.sqlite3")
    c = conn.cursor()
    for i in scoreBreakdownList:
        phone = i[0]
        scoreHeader = i[1]
        scoreRating = i[2]
        PlaceScoresInDatabase(phone, scoreHeader, scoreRating, conn, c)
    for i in phoneGoodBadBottomLineList:
        phone = i[0]
        description = i[1]
        sentiment = i[2]
        if sentiment == 'Like':
            UpdateProDatabase(phone, description, conn, c)
        elif sentiment == 'Good':
            UpdateProDatabase(phone, description, conn, c)
        elif sentiment == "Don't Like":
            UpdateConDatabase(phone, description, conn, c)
        elif sentiment == "Bad":
            UpdateConDatabase(phone, description, conn, c)
    # c.execute("DELETE FROM CellCheck_ProList")
    # conn.commit()
    # c.execute("DELETE FROM CellCheck_ConList")
    # conn.commit()
    # c.execute("DELETE FROM CellCheck_CNETDetailedScore")
    # conn.commit()
    conn.close()


# Start with the main function of the code
main()
