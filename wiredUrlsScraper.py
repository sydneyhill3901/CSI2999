import requests, time, json
from bs4 import BeautifulSoup

# parameters are:
# wired review archive url without page number, "https://www.wired.com/category/reviews/phones/page/"
# start page number (reviews begin on page 1, ordered most recent first)
# boolean indicating whether the entire archive should be scraped or just the given page

# writes pairs of phones and urls to json file
def getReviews(listPageRootUrl, pageNumber, isRecursive):
    currentPage = requests.get(listPageRootUrl + str(pageNumber))
    phoneDict = {}
    outputFile = open("wiredUrls.json", "w+", encoding="utf8")
    soup = BeautifulSoup(currentPage.content, "html.parser")
    articlesList = soup.find_all("li")
    for x in articlesList:
        try:
            lk = x.find('a', class_='clearfix pad')['href']
        except:
            pass                #easiest way to deal with "None" results

        headline = x.find('h2', string=lambda text: 'review' in text.lower())
        if headline != None:
            phoneName = headline.text.replace("Review:","").strip()
            if "and" in phoneName:
                pList = phoneName.replace(" and ", "@").split("@")
                for x in pList:
                    phoneDict[x] = lk
            else:
                phoneDict[phoneName] = lk
            time.sleep(1)

    if isRecursive:
        pageNumber += 1
        time.sleep(15)
        try:
            getReviews(listPageRootUrl, pageNumber, True)
        except:
            print("Reached end of reviews archive.")
    else:
        print("Reached end of reviews page.")

    jPhones = json.dumps(phoneDict)
    outputFile.write(jPhones)


#test
getReviews("https://www.wired.com/category/reviews/phones/page/", 1, False)