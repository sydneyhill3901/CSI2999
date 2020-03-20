import requests, time, csv
from bs4 import BeautifulSoup


# listPageRootUrl is "https://www.wired.com/category/reviews/phones/page/"
# pageNumber is the page number on Wired site to scrape
# write=True writes scraped URLs to CSV file in format phoneName|url
def getReviews(listPageRootUrl, pageNumber, write=True):
    currentPage = requests.get(listPageRootUrl + str(pageNumber))
    pageList = []
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("li")
    for y in x:
        try:
            link = y.find('a', class_='clearfix pad')['href']
        except:
            pass                #easiest way to deal with "None" results
        headline = y.find('h2', string=lambda text: 'review' in text.lower())
        if headline is not None:
            rowList = []
            phoneName = headline.text.replace("Review:","").lower().strip()
            if "and" in phoneName:
                pList = phoneName.replace(" and ", "@").split("@")
                for z in pList:
                    jList = []
                    try:
                        if int(z[0]) < 10 and int(z[0]) > 3 and z[1:6] == " plus":
                            z = "apple iphone " + z
                    except ValueError:
                        pass
                    jList.append(z)
                    jList.append(link)
                    pageList.append(z)
                    pageList.append(link)
                    if write:
                        writeCsvRow(jList)
            else:
                try:
                    if int(phoneName[0]) < 10 and int(phoneName[0]) > 3 and phoneName[1:6] == " plus":
                        phoneName = "apple iphone " + phoneName
                except ValueError:
                    pass
                rowList.append(phoneName)
                rowList.append(link)
                pageList.append(phoneName)
                pageList.append(link)
                if write:
                    writeCsvRow(rowList)
    return pageList


# pageNumber is the page number on Wired site to start scraping reviews from
# timeSleep is time to sleep in seconds between making each request
# if any interruption occurs, function can be called with pageNumber = page after the last page scraped before interruption
# csv writer will append to csv file as if no interruption occured
def writeAllReviews(listPageRootUrl, pageNumber, timeSleep):
    fullPhoneList = []
    startTime = time.time()
    if timeSleep < 3:
        timeSleep = 5
    timeSleep = float(timeSleep)
    while requests.get(listPageRootUrl + str(pageNumber)).ok:
        pagePhoneList = getReviews(listPageRootUrl, pageNumber)
        for x in pagePhoneList:
            fullPhoneList.append(x)
        print("Reviews on page " + str(pageNumber) + ":")
        print(pagePhoneList)
        fancySleep(timeSleep)
        pageNumber += 1
    print("Reached end of reviews.")
    print("RUNTIME: " + str(time.time() - startTime) + " seconds.")
    return fullPhoneList


# appends one row to CSV
def writeCsvRow(rowList):
    dataOutput = open("WiredURLs.csv", "a+", encoding="utf8")
    writer = csv.writer(dataOutput, delimiter='|', lineterminator="\r", quoting=csv.QUOTE_NONE)
    writer.writerow(rowList)


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


writeAllReviews("https://www.wired.com/category/reviews/phones/page/", 1, 10)