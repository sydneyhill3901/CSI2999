import requests, time, csv, sqlite3
from bs4 import BeautifulSoup
from sqlite3 import Error



# creates connection
def connect(dbFile):
    con = None
    try:
        con = sqlite3.connect(dbFile)
    except Error as e:
        print(e)
    return con


# scrapes every phone name on each page of phones on phone arena site and checks database for match
# if phoneName in Phones, specific phone page from phone arena is requested and scraped
# releaseDate is updated with scraped data
# timeSleep is time to sleep in seconds between making each request
def updatePhones(timeSleep):
    rootUrl = "https://www.phonearena.com/phones"
    nextPageUrl = "https://www.phonearena.com/phones/page/"
    print("Getting phones")
    updatePage(rootUrl, timeSleep)
    fancySleep(timeSleep)
    pageNum = 2
    while requests.get(nextPageUrl + str(pageNum)).ok:
        print("Getting phones on page " + str(pageNum))
        updatePage((nextPageUrl + str(pageNum)), timeSleep)
        fancySleep(timeSleep)
        pageNum += 1




# root url https://www.phonearena.com/phones
# next page url https://www.phonearena.com/phones/page/{pageNum}
# timeSleep is time to sleep in seconds between making each request
def updatePage(pageUrl, timeSleep):
    connection = connect("../CSI2999/db.sqlite3")
    cur = connection.cursor()
    menuHtml = requests.get(pageUrl)
    menuSoup = BeautifulSoup(menuHtml.content, "html.parser")
    y = menuSoup.find_all("div", class_="widget widget-tilePhoneCard")
    for z in y:
        phoneName = z.find("p", class_="title").text.lower().strip()
        url = z.find("a")['href']
        cur.execute("SELECT * FROM CellCheck_Phone WHERE PhoneName=?", (phoneName,))
        existingEntry = cur.fetchone()
        if existingEntry is not None:
            print("Match: " + phoneName)
            releaseDate = getReleaseDate(url)
            manufacturer = getManufacturer(url)
            print("Release Date: " + releaseDate)
            print("Manufacturer: " + manufacturer)
            cur.execute("UPDATE CellCheck_Phone SET ReleaseDate=? WHERE phoneName=?", (releaseDate, phoneName))
            cur.execute("UPDATE CellCheck_Phone SET Manufacturer=? WHERE phoneName=?", (manufacturer, phoneName))
            fancySleep(timeSleep)
            connection.commit()


# returns release date as string scraped from phonearena phone page url
def getReleaseDate(phonePageUrl):
    pageHtml = requests.get(phonePageUrl)
    pageSoup = BeautifulSoup(pageHtml.content, "html.parser")
    releaseDate = pageSoup.find("span", class_="meta-date").text
    return releaseDate


def getManufacturer(phonePageUrl):
    pageHtml = requests.get(phonePageUrl)
    pageSoup = BeautifulSoup(pageHtml.content, "html.parser")
    m = pageSoup.find("a", itemprop="item")
    n = m.find_next("a", itemprop="item")['href']
    manufacturerName = n.replace("https://www.phonearena.com/phones/manufacturers/", "")
    return manufacturerName

def fancySleep(timeSleep):
    print("sleeping " + str(int(timeSleep)) + " seconds", end="", flush=True)  # https://stackoverflow.com/questions/5598181/multiple-prints-on-the-same-line-in-python
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .")
    time.sleep(timeSleep / 4)


updatePhones(10)

#print(getReleaseDate("https://www.phonearena.com/phones/Samsung-Galaxy-S20+_id11289"))
