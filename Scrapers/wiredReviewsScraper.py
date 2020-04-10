import requests, time, csv, sqlite3
from bs4 import BeautifulSoup
from sqlite3 import Error



# Wired review object generated from web scrape
class WiredReview:
    def __init__(self, phoneName, url):
        self.phoneName = phoneName
        self.url = url
        self.soup = createSoup(url)
        self.score = getWiredReviewScore(self.soup)
        self.good = getWiredGood(self.soup)
        self.bad = getWiredBad(self.soup)


    def printReviewSummary(self):
        outputList = [self.phoneName, self.url, self.score, self.good, self.bad]
        return outputList

    def getScore(self):
        return self.score

    def getGood(self):
        return self.good

    def getBad(self):
        return self.bad

    def getUrl(self):
        return self.url


# review object created from data read in from a csv file of past web scrape
class LoadReview:
    def __init__(self, phoneName, url, score, good, bad):
        self.phoneName = phoneName
        self.url = url
        self.score = score
        self.good = good
        self.bad = bad


# function returns beautifulsoup soup from request html from reviewPageUrl
def createSoup(reviewPageUrl):
    reviewPage = requests.get(reviewPageUrl)
    reviewPageSoup = BeautifulSoup(reviewPage.content, "html.parser")
    return reviewPageSoup


# returns float score out of ten from soup
def getWiredReviewScore(reviewPageSoup):
    x = reviewPageSoup.find("li", class_="rating-review-component__rating")
    if x is None:
        return "NOSCORE"
    if "Rate" in x.text:
        scoreOutOfTen = float(x.text[4])
    return scoreOutOfTen


# three formats of wired reviews handled with three different functions
def getWiredGoodComponentFormA(reviewPageSoup):
    x = reviewPageSoup.find("li", class_="wired-tired-component__list-item wired-tired-component__list-item--pro")
    good = ""
    if x is not None:
        if "Wired" in x.text:
            good = x.find("span", class_="wired-tired-component__description").text.strip()
    return good

def getWiredGoodComponentFormB(reviewPageSoup):
    z = reviewPageSoup.find_all("h5", class_="brandon uppercase border-t")
    good = ""
    if z is not None:
        for a in z:
            if "Wired" in a.text:
                good = a.parent.find("p", class_="gray-5").text.strip()
    return good

def getWiredGoodComponentFormC(reviewPageSoup):
    y = reviewPageSoup.find_all("strong")
    good = ""
    for h in y:
        if h is not None:
            if "WIRED" in h.text:
                good = h.parent.text.replace("WIRED", "").strip()
    return good


# returns pros text from soup
def getWiredGood(reviewPageSoup):
    good = getWiredGoodComponentFormA(reviewPageSoup)
    if good == "":
        good = getWiredGoodComponentFormB(reviewPageSoup)
    if good == "":
        good = getWiredGoodComponentFormC(reviewPageSoup)
    return good


# three formats of wired reviews handled with three different functions
def getWiredBadComponentFormA(reviewPageSoup):
    x = reviewPageSoup.find("li", class_="wired-tired-component__list-item wired-tired-component__list-item--con")
    bad = ""
    if x is not None:
        if "Tired" in x.text:
            bad = x.find("span", class_="wired-tired-component__description").text.strip()
    return bad

def getWiredBadComponentFormB(reviewPageSoup):
    z = reviewPageSoup.find_all("h5", class_="brandon uppercase border-t")
    bad = ""
    if z is not None:
        for a in z:
            if "Wired" in a.text:
                good = a.parent.find("p", class_="gray-5")
                bad = good.find_next("p", class_="gray-5").text.strip()
    return bad

def getWiredBadComponentFormC(reviewPageSoup):
    y = reviewPageSoup.find_all("strong")
    bad = ""
    for h in y:
        if h is not None:
            if "TIRED" in h.text:
                bad = h.parent.text.replace("TIRED", "").strip()
    return bad


# returns cons text from soup
def getWiredBad(reviewPageSoup):
    bad = getWiredBadComponentFormA(reviewPageSoup)
    if bad == "":
        bad = getWiredBadComponentFormB(reviewPageSoup)
    if bad == "":
        bad = getWiredBadComponentFormC(reviewPageSoup)
    return bad



# urlCsv is csv file containing urls of wired reviews
# timeSleep is time to sleep in seconds between making each request
# calls writeCsv to write csv file from list of reviews created
def scrapeReviewsToCsv(urlCsv, timeSleep):
    sourceFile = open(urlCsv, "r", encoding="utf8")
    for row in sourceFile:
        outputList = []
        x = row.split(",")
        phoneName = x[0].strip()
        url = x[1].strip()
        print(phoneName)
        print(url)
        review = WiredReview(phoneName, url)
        if review.score != "NOSCORE":
            for x in review.printReviewSummary():
                outputList.append(x)
        fancySleep(timeSleep)
        writeCsv(outputList, "WiredScrapedData.csv")
    print("Reached end of reviews")


# urlCsv is csv file containing urls of wired reviews
# timeSleep is time to sleep in seconds between making each request
# returns dictionary of review objects where key is phoneName
def scrapeReviewsToDictionary(urlCsv, timeSleep):
    sourceFile = open(urlCsv, "r", encoding="utf8")
    outputDict = {}
    for row in sourceFile:
        x = row.split(",")
        phoneName = x[0].strip()
        url = x[1].strip()
        print(phoneName)
        print(url)
        review = WiredReview(phoneName, url)
        if review.score != "NOSCORE":
            outputDict[phoneName] = review
        fancySleep(timeSleep)
    print("Reached end of reviews")
    return outputDict


# creates a csv file containing scraped data
def writeCsv(outputList, csvFileName):
    dataOutput = open(csvFileName, "a+", encoding="utf8")
    writer = csv.writer(dataOutput, delimiter='|', lineterminator="\r")
    row = []
    for y in outputList:
        row.append(str(y))
    writer.writerow(row)


# for sleeping fancy
def fancySleep(timeSleep):
    print("sleeping " + str(int(timeSleep)) + " seconds", end="", flush=True)  # https://stackoverflow.com/questions/5598181/multiple-prints-on-the-same-line-in-python
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .")
    time.sleep(timeSleep / 4)


# creates connection
# https://www.sqlitetutorial.net/sqlite-python/insert/
def connect(dbFile):
    con = None
    try:
        con = sqlite3.connect(dbFile)
    except Error as e:
        print(e)
    return con


# inserts or updates data in all tables
def insertDataFromReview(connection, currentReview):
    insertPhone(connection, currentReview)
    insertRating(connection, currentReview)
    insertGood(connection, currentReview)
    insertBad(connection, currentReview)


# reads csv from backup CSV file to write to database
def insertDataFromCsv():
    phoneData = open("WiredDatatest.csv", encoding="utf8")
    reader = csv.reader(phoneData, delimiter='|')
    for row in reader:
        phoneName = row[0]
        url = row[1]
        score = row[2]
        good = row[3]
        bad = row[4]
        currentReview = LoadReview(phoneName, url, score, good, bad)
        connection = connect("../CSI2999/db.sqlite3")
        insertDataFromReview(connection, currentReview)


# urlCsv is CSV file containing scraped Wired URLs formatted phoneName|url
# timeSleep is time to sleep in seconds between making each request
# selectiveScrape is set to only scrape a review page if there is not an existing Wired review URL in a Phone entry
# selectiveScrape=False will scrape all Wired URLs in CSV file and insert or update data
# backupCsvWrite is set to create a CSV backup of all reviews scraped
def wiredScrapeAndInsert(urlCsv, timeSleep, selectiveScrape=True, backupCsvWrite=False):
    startTime = time.time()
    sourceFile = open(urlCsv, "r", encoding="utf8")
    connection = connect("../CSI2999/db.sqlite3")
    backupCsvName = "WiredScrapedDataBackup.csv"
    counter = 0
    cur = connection.cursor()
    for row in sourceFile:
        x = row.split("|")
        phoneName = x[0].strip().lower()
        url = x[1].strip()
        print(phoneName)
        try:
            if int(phoneName[0])<10 and int(phoneName[0])>3 and phoneName[1:6] == " plus":
                phoneName = "apple iphone " + phoneName
        except ValueError:
            pass
        print(url)
        scrape = False
        if selectiveScrape:
            cur.execute("SELECT WiredUrl FROM CellCheck_Phone WHERE PhoneName=?", (phoneName,))
            existingEntry = cur.fetchone()
            if existingEntry is None:
                scrape = True
            elif existingEntry[0] == "":
                print("Existing entry: " + str(existingEntry[0]))
                scrape = True
            else:
                scrape = False
                print("Existing entry: " + str(existingEntry[0]))
        else:
            scrape = True
        if scrape:
            review = WiredReview(phoneName, url)
            if review.score != "NOSCORE":
                insertDataFromReview(connection, review)
                if backupCsvWrite:
                    outputList = []
                    for x in review.printReviewSummary():
                        outputList.append(x)
                    writeCsv(outputList, backupCsvName)
                    counter += 1
            fancySleep(timeSleep)
    connection.commit()
    print("RUNTIME: " + str(time.time()-startTime) + " seconds.")
    print("PHONE REVIEWS SCRAPED: "+ str(counter))


# con is connection
# review is of type WiredReview or LoadReview
def insertPhone(con, review):
    cur = con.cursor()
    cur.execute("SELECT * FROM CellCheck_Phone WHERE PhoneName=?", (review.phoneName.lower().strip(),))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        sqlUpdate = "UPDATE CellCheck_Phone SET WiredURL=? WHERE phoneName=?"
        cur.execute(sqlUpdate, (review.url.strip(), review.phoneName.lower().strip()))
        cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
        phoneId = cur.fetchone()[0]
        print("Phone " + str(phoneId) + " " + review.phoneName.lower().strip()+ " updated")
    else:
        sqlInsert = "INSERT INTO CellCheck_Phone (PhoneName,CnetURL,WiredURL,PCMagURL,VergeURL,PhoneImageUrl,Manufacturer,ReleaseDate) VALUES(?,?,?,?,?,?,?,?)"
        cur.execute(sqlInsert, (review.phoneName.lower().strip(), "", review.url, "", "", "", "", ""))
        cur.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (review.phoneName.lower().strip(),))
        phoneId = cur.fetchone()[0]
        print("Phone " + str(phoneId) + " " + review.phoneName.lower().strip() + " added")
    con.commit()


# con is connection
# review is of type WiredReview or LoadReview
def insertRating(con, review, update=True):
    cur = con.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("Wired",))
    wiredId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
    phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_Rating WHERE Site_id=? AND Phone_id=?", (wiredId, phoneId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        if update:
            sqlUpdate = "UPDATE CellCheck_Rating SET Rating=? WHERE Site_id=? AND Phone_id=?"
            cur.execute(sqlUpdate, (review.score, wiredId, phoneId,))
            print("Rating updated")
        else:
            print("Rating already exists")
    else:
        sqlInsert = "INSERT INTO CellCheck_Rating (Rating,Phone_id,Site_id) VALUES(?,?,?)"
        print(review.score)
        cur.execute(sqlInsert, (review.score,phoneId,wiredId,))
        print("Rating added")
    con.commit()


# con is connection
# review is of type WiredReview or LoadReview
def insertGood(con, review, update=True):
    cur = con.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("Wired",))
    wiredId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
    phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_Prolist WHERE Site_id=? AND Phone_id=?", (wiredId, phoneId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        if update:
            sqlUpdate = "UPDATE CellCheck_Prolist SET Pros=? WHERE Site_id=? AND Phone_id=?"
            cur.execute(sqlUpdate, (review.good, wiredId, phoneId,))
            print("Pros entry updated")
        else:
            print("Pros entry already exists")
    else:
        sqlInsert = "INSERT INTO CellCheck_Prolist (Phone_id,Site_id,Pros) VALUES(?,?,?) "
        cur.execute(sqlInsert, (phoneId, wiredId, review.good,))
        print("Pros entry added")
    con.commit()


# con is connection
# review is of type WiredReview or LoadReview
def insertBad(con, review, update=True):
    cur = con.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("Wired",))
    wiredId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
    phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_Conlist WHERE Site_id=? AND Phone_id=?", (wiredId, phoneId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        if update:
            sqlUpdate = "UPDATE CellCheck_Conlist SET Cons=? WHERE Site_id=? AND Phone_id=?"
            cur.execute(sqlUpdate, (review.bad, wiredId, phoneId,))
            print("Cons entry updated")
        else:
            print("Cons entry already exists")
    else:
        sqlInsert = "INSERT INTO CellCheck_Conlist (Phone_id,Site_id,Cons) VALUES(?,?,?) "
        cur.execute(sqlInsert, (phoneId, wiredId, review.bad,))
        print("Cons entry added")
    con.commit()



wiredScrapeAndInsert("WiredURLs.csv", 10)


