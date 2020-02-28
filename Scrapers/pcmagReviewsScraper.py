import requests, time
from bs4 import BeautifulSoup

# if we return "good" and "bad" as lists, use a different delimiter for csv output
class PCMagReview:
    def __init__(self, phoneName, url):
        self.phoneName = phoneName
        self.url = url
        self.soup = createSoup(url)
        self.score = getPCmagReviewScore(self.soup)
        self.good = str(getPCmagGood(self.soup))
        self.bad = str(getPCmagBad(self.soup))

    def printReviewSummary(self):
        outputList = [self.phoneName, self.url, self.score, self.good, self.bad]
        return outputList


def createSoup(reviewPageUrl):
    reviewPage = requests.get(reviewPageUrl)
    reviewPageSoup = BeautifulSoup(reviewPage.content, "html.parser")
    return reviewPageSoup

def getPCmagReviewScore(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="flex flow-row justify-center content-center mr-2")
    scoreOutOfTen = float(x.text.strip())*2
    return scoreOutOfTen

def getPCmagGood(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="w-full md:w-1/2")
    prosList = []
    if "Pros" in x.text:
        gList = x.find_all("li", class_="flex mb-2 items-baseline leading-loose")
        for m in gList:
            prosList.append(m.text)
    return prosList

def getPCmagBad(reviewPageSoup):
    x = reviewPageSoup.find("div", class_="w-full md:w-1/2 md:pl-4")
    consList = []
    if "Cons" in x.text:
        bList = x.find_all("li", class_="flex mb-2 items-baseline leading-loose")
        for m in bList:
            consList.append(m.text)
    return consList


def printReviewSummary(phoneName, reviewPageUrl):
    soup = createSoup(reviewPageUrl)
    score = getPCmagReviewScore(soup)
    good = getPCmagGood(soup)
    bad = getPCmagBad(soup)
    outputList = [phoneName, reviewPageUrl, score, good, bad]
    return outputList

# format phoneName, url
def scrapeReviews(urlCsv, timeSleep):
    sourceFile = open(urlCsv, "r", encoding="utf8")
    outputFile = open("PCmagData.csv", "a+", encoding="utf8")
    outputList = []
    for row in sourceFile:
        x = row.split(",")
        phoneName = x[0].strip()
        url = x[1].strip()
        print(phoneName)
        print(url)
        review = PCMagReview(phoneName, url)
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




#test
scrapeReviews("PCmagURLs.csv", 10)
