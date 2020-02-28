import requests, time
from bs4 import BeautifulSoup


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

def createSoup(reviewPageUrl):
    reviewPage = requests.get(reviewPageUrl)
    reviewPageSoup = BeautifulSoup(reviewPage.content, "html.parser")
    return reviewPageSoup

def getWiredReviewScore(reviewPageSoup):
    x = reviewPageSoup.find("li", class_="rating-review-component__rating")
    if x is None:
        return "NOSCORE"
    if "Rate" in x.text:
        scoreOutOfTen = float(x.text[4])
    return scoreOutOfTen

def getWiredGood(reviewPageSoup):
    x = reviewPageSoup.find("li", class_="wired-tired-component__list-item wired-tired-component__list-item--pro")
    if x is None:
        return ""
    if "Wired" in x.text:
        y = x.find("span", class_="wired-tired-component__description").text
        return y

def getWiredBad(reviewPageSoup):
    x = reviewPageSoup.find("li", class_="wired-tired-component__list-item wired-tired-component__list-item--con")
    if x is None:
        return ""
    if "Tired" in x.text:
        y = x.find("span", class_="wired-tired-component__description").text
        return y

def scrapeReviews(urlCsv, timeSleep):
    sourceFile = open(urlCsv, "r", encoding="utf8")
    outputFile = open("WiredData.csv", "a+", encoding="utf8")
    outputList = []
    for row in sourceFile:
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
    print("Reached end of reviews")
    for y in outputList:
        outputFile.write(str(y) + ",")

def fancySleep(timeSleep):
    print("sleeping " + str(int(timeSleep)) + " seconds", end="", flush=True)  # https://stackoverflow.com/questions/5598181/multiple-prints-on-the-same-line-in-python
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .")
    time.sleep(timeSleep / 4)




scrapeReviews("WiredURLs.csv", 10)






