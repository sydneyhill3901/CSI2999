import requests, time, sqlite3
from sqlite3 import Error
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import NoSuchElementException


# customer review object
class customerReview:
    def __init__(self, phoneName, manufacturer, link, score, title, content, useful):
        self.name = phoneName
        self.manufacturer = manufacturer
        self.url = link
        self.score = float(score)
        self.title = title
        self.content = content
        self.isPositive = self.score >= 4
        self.useful = useful


# headlessness=True can be set to False in test mode
def startBrowser(headlessness=True):
    fireFoxOptions = webdriver.FirefoxOptions()
    fireFoxOptions.headless = headlessness
    browser = webdriver.Firefox(options=fireFoxOptions)
    return browser



# timeSleep = time to sleep in seconds between page requests
# testmode is set to True to enable visible browser windows and longer load times
# waitfactor=1 sets the wait time between click events in selenium to between 1 and 3 seconds per event
# (8 seconds wait total for waitfactor=1)
# increasing waitFactor increases the wait time pre event by a factor of (waitFactor)
def getSprintUserReviews(timeSleep, testmode=False, waitFactor=1):
    currentPage = requests.get("https://www.sprint.com/en/shop/cell-phones.html?INTNAV=TopNav:V4:Shop:Phones&credit=undefined&sort=FEATURED")
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("div", class_="device-full__tile px-md-20 pt-20")
    for y in x:
        try:
            z = y.find("div", class_="row devicetitlecontainer__wall")
            a = z.find("h3")
            link = "https://www.sprint.com/" + z.find("a")['href'].strip()
            manufacturer = a.find("span", class_="font-size-12 devicetilewall__device-manufacturer color--gray-dark").text.strip()
            phoneName = a.find("span", class_="font-size-18").text.strip()
            line3 = a.text.replace(manufacturer, "").replace(phoneName, "").strip().lower()
            phoneName = phoneName.replace("+", " plus")
            if line3 == "":
                phoneName = manufacturer + " " + phoneName
                print(phoneName + ": " + link)
                getMostHelpful(link, phoneName, manufacturer, testmode, waitFactor)
            elif "pre-owned" in line3:
                pass
            else:
                phoneName = manufacturer + " " + phoneName
                phoneName = phoneName + " " + line3
                print(phoneName + ": " + link)
                getMostHelpful(link, phoneName, manufacturer, testmode, waitFactor)
            fancySleep(timeSleep)
        except AttributeError:
            pass


def addReview(elementSoup, phoneName, manufacturer, link, connection):
    try:
        title = elementSoup.find("div", class_="tt-c-review__heading tt-u-mb--sm").text.strip()
    except AttributeError:
        title = ""
    try:
        content = elementSoup.find("div", class_="tt-c-review__text").text.strip()
        useful = int(elementSoup.find("span", class_="tt-c-review-toolbar__likes-number").text.strip())
        score = int(elementSoup.find("div", class_="tt-c-rating tt-c-review__rating tt-u-mb--sm").text.strip()[6])
        currentReview = customerReview(phoneName, manufacturer, link, score, title, content, useful)
        insertUserReview(currentReview, connection)
    except AttributeError:
        pass


# creates connection
# https://www.sqlitetutorial.net/sqlite-python/insert/
def connect(dbFile):
    con = None
    try:
        con = sqlite3.connect(dbFile)
    except Error as e:
        print(e)
    return con


# inserts the review into the database
# creates a new phone in Phones table if no match exists
def insertUserReview(review, connection):
    cur = connection.cursor()
    phoneName = review.name.lower()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("Sprint",))
    sprintId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (phoneName,))
    phone = cur.fetchone()
    if phone is not None:
        phoneId = phone[0]
    else:
        sqlInsert = "INSERT INTO CellCheck_Phone (PhoneName,CnetURL,WiredURL,PCMagURL,VergeURL,PhoneImageUrl,Manufacturer,ReleaseDate) VALUES(?,?,?,?,?,?,?,?)"
        cur.execute(sqlInsert, (phoneName, "", "", "", "", "", "", "",))
        cur.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (phoneName,))
        phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_UserReview WHERE Phone_id=? AND Site_id=? AND Content=?", (phoneId, sprintId, review.content,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        cur.execute("UPDATE CellCheck_UserReview SET Rating=?, isPositive=?, Title=? WHERE Phone_id=? AND Site_id=? AND Content=?", (review.score, review.isPositive, review.title, phoneId, sprintId, review.content,))
        print("User review for " + review.name + " updated")
        print(review.title + ": " + str(int(review.score)) + " out of 5")
    else:
        sqlInsert = "INSERT INTO CellCheck_UserReview (Site_id, Phone_id, UsefulCount, isPositive, Rating, Content, Title) VALUES(?,?,?,?,?,?,?)"
        cur.execute(sqlInsert, (sprintId, phoneId, review.useful, review.isPositive, review.score, review.content, review.title,))
        print("User review for " + review.name + " added")
        print(review.title + ": " + str(int(review.score)) + " out of 5")
    connection.commit()


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


def insertAvgUserScore(score, phoneName, connection):
    cur = connection.cursor()
    cur.execute("SELECT id FROM CellCheck_Site WHERE siteName=?", ("Sprint",))
    sprintId = cur.fetchone()[0]
    cur.execute("SELECT id FROM CellCheck_Phone WHERE phoneName=?", (phoneName,))
    phone = cur.fetchone()
    if phone is not None:
        phoneId = phone[0]
    else:
        sqlInsert = "INSERT INTO CellCheck_Phone (PhoneName,CnetURL,WiredURL,PCMagURL,VergeURL,PhoneImageUrl,Manufacturer,ReleaseDate) VALUES(?,?,?,?,?,?,?,?)"
        cur.execute(sqlInsert, (phoneName, "", "", "", "", "", "", "",))
        cur.execute("SELECT id FROM CellCheck_Phone WHERE PhoneName=?", (phoneName,))
        phoneId = cur.fetchone()[0]
    cur.execute("SELECT * FROM CellCheck_AvgUserScore WHERE Phone_id=? AND Site_id=?", (phoneId, sprintId,))
    existingEntry = cur.fetchone()
    if existingEntry is not None:
        cur.execute("UPDATE CellCheck_AvgUserScore SET AvgScore=? WHERE Phone_id=? AND Site_id=?", (phoneId, sprintId, score,))
        print("Average user rating for " + phoneName + ": " + str(score) + " updated")
    else:
        cur.execute("INSERT INTO CellCheck_AvgUserScore (Phone_id, Site_id, AvgScore) VALUES (?,?,?)", (phoneId, sprintId, score,))
        print("Average user rating for " + phoneName + ": " + str(score) + " added")
    connection.commit()


# a very messy method created by following realpython example
# takes the URL of the page containing the product and reviews, the phoneName and manufacturer
# waitFactor can be increased if there are errors gathering the reviews
# waitfactor=1 will cause selenium to wait 1-3 seconds after each click for the page to load the element
# creates headless browser, adds to database, then quits browser
""" 
If this method is run and stopped before the headless browser quits, firefox instance remains open.
"""
def getMostHelpful(productPageUrl, phoneName, manufacturer, testmode=False, waitFactor=1):     #https://realpython.com/modern-web-automation-with-python-and-selenium/
    print("Getting most helpful reviews for the " + phoneName)
    connection = connect("../CSI2999/db.sqlite3")
    if testmode:
        w = 2*waitFactor
        headlessBrowser=startBrowser(False)
    else:
        w = waitFactor
        headlessBrowser = startBrowser()
    failCountDown = 3               #number of retries before reporting error
    while failCountDown > 0:
        try:
            headlessBrowser.get(productPageUrl)
            time.sleep(w)
            element = headlessBrowser.find_element_by_id("tab-menu-review")
            headlessBrowser.execute_script("arguments[0].click()", element)
            time.sleep(3*w)
            avgUserScoreElem = headlessBrowser.find_element_by_class_name("tt-c-reviews-summary__rating-number")
            time.sleep(w)
            menuElem = headlessBrowser.find_element_by_class_name("tt-c-reviews-list-toolbar__sort-text")
            headlessBrowser.execute_script("arguments[0].click()", menuElem)
            time.sleep(2*w)
            mostHelpful = headlessBrowser.find_element_by_class_name("tt-o-menu__item-title")
            headlessBrowser.execute_script("arguments[0].click()", mostHelpful)
            time.sleep(w)
            reviews = headlessBrowser.find_elements_by_class_name("tt-c-review")
            failCountDown = 0
        except NoSuchElementException:  #selenium couldn't find the thing so we let it try again, up to 3 tries
            if failCountDown == 1:      #on the last try report that no review elements could be found
                print("Error occurred while locating review elements.")
            failCountDown -= 1
    x = 0                           #index of review element that has not been added yet
    try:                            #nasty try except block needed to attempt to get the reviews if they exist
        insertAvgUserScore(float(avgUserScoreElem.text), phoneName.lower(), connection)    # insert average user score to AvgUserScore table
        while x < len(reviews):     #counter to grab every review
            try:                    #try to grab review information from element
                soup = BeautifulSoup(reviews[x].get_attribute("innerHTML"), "html.parser")  #each review element is a soup
                addReview(soup, phoneName, manufacturer, productPageUrl, connection)
                x += 1              #increment to index of next review to be added
            except StaleElementReferenceException:  # if element reference is stale, refresh and start from index of next review
                reviews = headlessBrowser.find_elements_by_class_name("tt-c-review")
                time.sleep(1)
    except UnboundLocalError:       #if reviews wasn't assigned because no review elements were found, quit without adding
        print("No reviews were found for the " + phoneName)
    headlessBrowser.quit()




"""
If there are errors, increase waitFactor.
If the program is run outside of testmode and stopped (or if it terminates due to an error)
headless Firefox instances will need to be closed from windows task manager.
"""

getSprintUserReviews(timeSleep=10, testmode=False, waitFactor=1)
