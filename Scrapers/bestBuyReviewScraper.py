import requests, time, csv
from bs4 import BeautifulSoup

# rootUrl = https://www.bestbuy.com/site/mobile-cell-phones/unlocked-mobile-phones/pcmcat156400050037.c?id=pcmcat156400050037


class customerReview:
    def __init__(self, phoneName, manufacturer, link, score, title, content):
        self.name = phoneName
        self.manufacturer = manufacturer
        self.url = link
        self.score = score
        self.title = title
        self.content = content

# requests a single page, no sleep timer
# returns a dict with manufacturer name as key, url as value
def getManufacturerPages(rootUrl):
    manufacturerDict = {}
    currentPage = requests.get(rootUrl, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) hrome/23.0.1271.64 Safari/537.11'})
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("div", class_="flex-copy-wrapper")
    for y in x:
        link = "https://www.bestbuy.com/" + y.find("a")['href']
        name = y.find("a")['linktext']
        manufacturerDict[name] = link
    return manufacturerDict

# creates one request when called
# calls two functions which make one request each in a loop
# total wait time is 2 * timeSleep * number of model pages
# returns a dict with phone name as key, review page url as value
def getModelPages(link, timeSleep):
    modelDict = {}
    currentPage = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) hrome/23.0.1271.64 Safari/537.11'})
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("section", class_="lv facet")
    for y in x:
        category = y.find("span", class_="c-section-title-text").text
        if category == "Model Family":
            z = y.find_all("label")
            for a in z:
                name = a.find("span", class_="facet-option-label-text").text
                print(name)
                lk = a.find("a")['href']
                productLink = getProductPage(lk)
                fancySleep(timeSleep)
                reviewLink = getReviewPage(productLink)
                fancySleep(timeSleep)
                modelDict[name] = reviewLink

    return modelDict


# gets first product listed on model page and returns its product page link
def getProductPage(link):
    currentPage = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) hrome/23.0.1271.64 Safari/537.11'})
    print(currentPage)
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find("div", class_="list-item lv")
    y = x.find("h4", class_="sku-header")
    lk = "https://www.bestbuy.com/" + y.find("a")['href']
    return lk


# gets 'see all reviews' page link on product page
def getReviewPage(link):
    currentPage = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) hrome/23.0.1271.64 Safari/537.11'})
    print(currentPage)
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find("div", class_="user-generated-content-ratings-and-reviews")
    y = x.find("div", class_="col-xs-12 component-wrapper")
    lk = "https://www.bestbuy.com/" + y.find("a", class_="see-all-reviews")['href']
    return lk

# collects information from verified user reviews on review page link
# makes a single request so no sleep time
# returns a list of customerReview objects
def getReviews(link, phoneName, manufacturer):
    reviewList = []
    currentPage = requests.get(link, headers={'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) hrome/23.0.1271.64 Safari/537.11'})
    print(currentPage)
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("li", class_="review-item")
    for y in x:
        verified = y.find("div", class_="verified-purchaser-mv-wrapper")
        if verified.text == "Verified Purchase|":
            z = y.find("div", class_="review-heading")
            title = z.find("h4").text
            a = y.find("div", class_="ugc-review-body body-copy-lg")
            c = a.find("p").text
            content = c.replace("\r", " ").replace("\n", " ")
            b = y.find("div", class_="c-ratings-reviews-v2 v-small")
            rating = b.find("p").text[6]
            currentReview = customerReview(phoneName, manufacturer, link, rating, title, content)
            reviewList.append(currentReview)
    return reviewList


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


def collectAllBestBuyReviews(rootUrl, timeSleep):
    startTime = time.time()
    reviewList = []
    manufacturerPages = getManufacturerPages(rootUrl)
    for manufacturerName in manufacturerPages:
        print(manufacturerName)
        print(manufacturerPages[manufacturerName])
        modelPages = getModelPages(manufacturerPages[manufacturerName], timeSleep)
        for phoneName in modelPages:
            print(phoneName)
            print(modelPages[phoneName])
            pageReviewList = getReviews(modelPages[phoneName], phoneName, manufacturerName)
            for review in pageReviewList:
                reviewList.append(review)
            time.sleep(timeSleep)
    runTime = time.time() - startTime
    print("RUNTIME:" + str(runTime) + " seconds")
    return reviewList


def outputToCsv(reviewList):
    dataOutput = open("BestBuyReviews.csv", "a+", encoding="utf8")
    writer = csv.writer(dataOutput, delimiter='|', lineterminator="\r")
    for y in reviewList:
        row = []
        row.append(y.name)
        row.append(y.manufacturer)
        row.append(y.url)
        row.append(y.score)
        row.append(y.title)
        row.append(y.content)
        writer.writerow(row)


# tests
#print(getManufacturerPages("https://www.bestbuy.com/site/mobile-cell-phones/unlocked-mobile-phones/pcmcat156400050037.c?id=pcmcat156400050037"))
#print(getModelPages("https://www.bestbuy.com//site/iphone/iphone-unlocked-phones/pcmcat1542305802014.c?id=pcmcat1542305802014", 10))
#print(getReviews("https://www.bestbuy.com//site/reviews/apple-iphone-11-with-64gb-memory-cell-phone-unlocked-purple/6223312?variant=A", "iphone11", "apple"))
#outputToCsv(getReviews("https://www.bestbuy.com/site/reviews/motorola-moto-one-action-with-128gb-memory-cell-phone-unlocked-denim-blue/6375633?variant=A", "iphone11", "apple"))


# run
outputToCsv(collectAllBestBuyReviews("https://www.bestbuy.com/site/mobile-cell-phones/unlocked-mobile-phones/pcmcat156400050037.c?id=pcmcat156400050037", 10))