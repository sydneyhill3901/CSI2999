import requests, time, csv, sqlite3
from bs4 import BeautifulSoup
from sqlite3 import Error



# pcmag review object generated from web scrape
class PCMagReview:
    def __init__(self, phoneName, url):
        self.phoneName = phoneName
        self.url = url
        self.soup = createSoup(url)
        self.score = getPCmagReviewScore(self.soup)
        self.good = getPCmagGood(self.soup)
        self.bad = getPCmagBad(self.soup)
        self.image = getPhotoLink(self.soup)

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

    # returns image url from pcmag review
    def getImage(self):
        return self.image


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
def getPCmagReviewScore(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="flex flow-row justify-center content-center mr-2")
    if x is not None:
        scoreOutOfTen = float(x.text.strip())*2
    else:
        scoreOutOfTen = "NOSCORE"
    return scoreOutOfTen

# returns pros as a string
# can be formatted as a list by changing join character
def getPCmagGood(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="w-full md:w-1/2")
    prosList = []
    if "Pros" in x.text:
        gList = x.find_all("li", class_="flex mb-2 items-baseline leading-loose")
        for m in gList:
            prosList.append(m.text)
        pros = " ".join(prosList)       # change join character here
    return pros

# returns cons as a string
# can be formatted as a list by changing join character
def getPCmagBad(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="w-full md:w-1/2 md:pl-4")
    consList = []
    if "Cons" in x.text:
        bList = x.find_all("li", class_="flex mb-2 items-baseline leading-loose")
        for m in bList:
            consList.append(m.text)
        cons = " ".join(consList)       # change join character here
    return cons

# returns photo link
def getPhotoLink(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="relative")
    y = x.find_next("div", class_="relative")
    z = y.find_next("div", class_="relative")
    a = z.find_next("div", class_="relative")
    b = a.find_next("div", class_="relative")
    c = b.find_next("div", class_="relative")
    d = c.find_next("div", class_="relative")
    e = d.find("img")['src']
    return e



# urlCsv is csv file containing urls of pcmag reviews
# timeSleep is time to sleep in seconds between making each request
# calls writeCsv to write csv file from list of reviews created
def scrapeReviewstoCsv(urlCsv, timeSleep):
    sourceFile = open(urlCsv, "r", encoding="utf8")
    outputList = []
    for row in sourceFile:
        x = row.split("|")
        phoneName = x[0].strip()
        url = x[1].strip()
        print(phoneName)
        print(url)
        review = PCMagReview(phoneName, url)
        if review.score != "NOSCORE":
            for x in review.printReviewSummary():
                outputList.append(x)
        fancySleep(timeSleep)
        writeCsv(outputList, "PCMagData.csv")
    print("Reached end of reviews")


# urlCsv is csv file containing urls of pcmag reviews
# timeSleep is time to sleep in seconds between making each request
# returns dictionary of review objects where key is phoneName
def scrapeReviewsToDictionary(urlCsv, timeSleep):
    sourceFile = open(urlCsv, "r", encoding="utf8")
    outputDict = {}
    for row in sourceFile:
        x = row.split("|")
        phoneName = x[0].strip()
        url = x[1].strip()
        print(phoneName)
        print(url)
        review = PCMagReview(phoneName, url)
        if review.score != "NOSCORE":
            outputDict[phoneName] = review
        fancySleep(timeSleep)
    print("Reached end of reviews")
    return outputDict


# creates a csv file containing scraped data
def writeCsv(outputList, csvFileName):
    dataOutput = open(csvFileName, "a+", encoding="utf8")
    writer = csv.writer(dataOutput, delimiter='|', lineterminator="\r", quoting=csv.QUOTE_NONE)
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
    phoneData = open("PCMagScrapedDataBackup.csv", encoding="utf8")
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


# urlCsv is CSV file containing scraped PCmag URLs formatted phoneName|url
# timeSleep is time to sleep in seconds between making each request
# selectiveScrape is set to only scrape a review page if there is not an existing PCMag review URL in a Phone entry
# selectiveScrape=False will scrape all PCmag URLs in CSV file and insert or update data
# backupCsvWrite is set to create a CSV backup of all reviews scraped
def pcmagScrapeAndInsert(urlCsv, timeSleep, selectiveScrape=True, backupCsvWrite=False):
    startTime = time.time()
    sourceFile = open(urlCsv, "r", encoding="utf8")
    connection = connect("../CSI2999/db.sqlite3")
    backupCsvName = "PCMagScrapedDataBackup.csv"
    counter = 0
    cur = connection.cursor()
    for row in sourceFile:
        x = row.split("|")
        phoneName = x[0].strip().lower()
        if "+" in phoneName:
            phoneName = phoneName.replace("+", " plus")
        url = x[1].strip()
        phoneName = phoneName.replace("+", " plus").replace("(", "").replace(")", "")
        print(phoneName)
        print(url)
        scrape = False
        if selectiveScrape:
            cur.execute("SELECT PCMagURL FROM CellCheck_Phone WHERE PhoneName=?", (phoneName,))
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
            review = PCMagReview(phoneName, url)
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
# review is of type PCMagReview or LoadReview
def insertPhone(con, review):
    cur = con.cursor()
    cur.execute("SELECT * FROM CellCheck_Phone WHERE PhoneName=?", (review.phoneName,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        sqlUpdate = "UPDATE CellCheck_Phone SET PCMagURL=? WHERE phoneName=?"
        cur.execute(sqlUpdate, (review.url.strip(), review.phoneName.lower().strip()))
        cur.execute("SELECT PhoneImageUrl FROM CellCheck_Phone WHERE PhoneName=?", (review.phoneName,))
        phoneImg = cur.fetchone()[0]
        if phoneImg == "":
            cur.execute("UPDATE CellCheck_Phone SET PhoneImageUrl=? WHERE PhoneName=?", (review.image, review.phoneName,))
        cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName,))
        phoneId = cur.fetchone()[0]
        print("Phone " + str(phoneId) + " " + review.phoneName.lower().strip()+ " updated")

    else:
        sqlInsert = "INSERT INTO CellCheck_Phone (PhoneName,CnetURL,WiredURL,PCMagURL,VergeURL,PhoneImageUrl,Manufacturer,ReleaseDate) VALUES(?,?,?,?,?,?,?,?)"
        cur.execute(sqlInsert, (review.phoneName, "", "", review.url, "", review.image, "", ""))
        cur.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (review.phoneName.lower().strip(),))
        phoneId = cur.fetchone()[0]
        print("Phone " + str(phoneId) + " " + review.phoneName.lower().strip() + " added")
    con.commit()


# con is connection
# review is of type PCMagReview or LoadReview
def insertRating(con, review, update=True):
    cur = con.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("PCMag",))
    pcmagId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
    phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_Rating WHERE Site_id=? AND Phone_id=?", (pcmagId, phoneId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        if update:
            sqlUpdate = "UPDATE CellCheck_Rating SET Rating=? WHERE Site_id=? AND Phone_id=?"
            cur.execute(sqlUpdate, (review.score, pcmagId, phoneId,))
            print("Rating updated")
        else:
            print("Rating already exists")
    else:
        sqlInsert = "INSERT INTO CellCheck_Rating (Rating,Phone_id,Site_id) VALUES(?,?,?)"
        print(review.score)
        cur.execute(sqlInsert, (review.score, phoneId, pcmagId,))
        print("Rating added")
    con.commit()


# con is connection
# review is of type PCMagReview or LoadReview
def insertGood(con, review, update=True):
    cur = con.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("PCMag",))
    pcmagId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
    phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_Prolist WHERE Site_id=? AND Phone_id=?", (pcmagId, phoneId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        if update:
            sqlUpdate = "UPDATE CellCheck_Prolist SET Pros=? WHERE Site_id=? AND Phone_id=?"
            cur.execute(sqlUpdate, (review.good, pcmagId, phoneId,))
            print("Pros entry updated")
        else:
            print("Pros entry already exists")
    else:
        sqlInsert = "INSERT INTO CellCheck_Prolist (Phone_id,Site_id,Pros) VALUES(?,?,?) "
        cur.execute(sqlInsert, (phoneId, pcmagId, review.good,))
        print("Pros entry added")
    con.commit()


# con is connection
# review is of type PCMagReview or LoadReview
def insertBad(con, review, update=True):
    cur = con.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("PCMag",))
    pcmagId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (review.phoneName.lower().strip(),))
    phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_Conlist WHERE Site_id=? AND Phone_id=?", (pcmagId, phoneId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        if update:
            sqlUpdate = "UPDATE CellCheck_Conlist SET Cons=? WHERE Site_id=? AND Phone_id=?"
            cur.execute(sqlUpdate, (review.bad, pcmagId, phoneId,))
            print("Cons entry updated")
        else:
            print("Cons entry already exists")
    else:
        sqlInsert = "INSERT INTO CellCheck_Conlist (Phone_id,Site_id,Cons) VALUES(?,?,?) "
        cur.execute(sqlInsert, (phoneId, pcmagId, review.bad,))
        print("Cons entry added")
    con.commit()



pcmagScrapeAndInsert("PCMagURLs.csv", 10)