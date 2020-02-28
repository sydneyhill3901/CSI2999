import requests, time
from bs4 import BeautifulSoup


def getReviews(listPageRootUrl, pageNumber):
    currentPage = requests.get(listPageRootUrl + str(pageNumber))
    phoneList = []
    soup = BeautifulSoup(currentPage.content, "html.parser")
    x = soup.find_all("div", class_="w-full flex flex-wrap md:flex-no-wrap py-4 border-b border-gray-lighter")
    for y in x:
        z = y.find("span", class_="ml-1 mr-3")
        if z is not None:
            k = y.find("h2", class_="text-base md:text-xl font-brand font-bold")
            link = "https://www.pcmag.com/" + k.find("a")['href']
            p = k.find("a")['data-item']
            phoneName = p.replace(" Review", "")
            phoneList.append(phoneName)
            phoneList.append(link)
    return phoneList

def getAllReviews(listPageRootUrl, pageNumber, timeSleep):
    fullPhoneList = []
    if timeSleep < 3:
        timeSleep = 5
    timeSleep = float(timeSleep)
    while requests.get(listPageRootUrl + str(pageNumber)).ok:
        pagePhoneList = getReviews(listPageRootUrl, pageNumber)
        for x in pagePhoneList:
            fullPhoneList.append(x)
        print(pagePhoneList)
        fancySleep(timeSleep)
        pageNumber += 1
    print("Reached end of reviews.")
    return fullPhoneList

def printCsv(fullPhoneList):
    wOutput = open("PCmagURLs.csv", "w+", encoding="utf8")
    endIndex = len(fullPhoneList)
    for n in range(int(endIndex/2)):
        phoneName = str(fullPhoneList[n*2])
        phoneUrl = str(fullPhoneList[(n*2)+1])
        wOutput.write(phoneName + "," + phoneUrl + "\n")


def fancySleep(timeSleep):
    print("sleeping " + str(int(timeSleep)) + " seconds", end="", flush=True)  # https://stackoverflow.com/questions/5598181/multiple-prints-on-the-same-line-in-python
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .", end="", flush=True)
    time.sleep(timeSleep / 4)
    print(" .")
    time.sleep(timeSleep / 4)



printCsv(getAllReviews("https://www.pcmag.com/categories/mobile-phones?page=", 1, 10))
