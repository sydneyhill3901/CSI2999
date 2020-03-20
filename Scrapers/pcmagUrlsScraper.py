import requests, time, csv
from bs4 import BeautifulSoup


# listPageRootUrl is "https://www.pcmag.com/categories/mobile-phones?page="
# pageNumber is the page number on PCMag site to scrape
# write=True writes scraped URLs to CSV file in format phoneName|url
def getReviews(listPageRootUrl, pageNumber, write=True):
    pageList = []
    currentPage = requests.get(listPageRootUrl + str(pageNumber))
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("div", class_="w-full flex flex-wrap md:flex-no-wrap py-4 border-b border-gray-lighter")
    for y in x:
        z = y.find("span", class_="ml-1 mr-3")
        if z is not None:
            rowList = []
            k = y.find("h2", class_="text-base md:text-xl font-brand font-bold")
            link = "https://www.pcmag.com" + k.find("a")['href']
            p = k.find("a")['data-item']
            phoneName = p.replace(" Review", "").lower().strip()
            if "(" in phoneName and ")" in phoneName:
                q = phoneName.split("(")
                phoneName = q[0].strip()
            rowList.append(phoneName)
            rowList.append(link)
            pageList.append(phoneName)
            pageList.append(link)
            if write:
                writeCsvRow(rowList)
    return pageList


# listPageRootUrl is "https://www.pcmag.com/categories/mobile-phones?page="
# pageNumber is the page number on PCMag site to start scraping reviews from
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
    dataOutput = open("PCMagURLs.csv", "a+", encoding="utf8")
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



writeAllReviews("https://www.pcmag.com/categories/mobile-phones?page=", 1, 10)
