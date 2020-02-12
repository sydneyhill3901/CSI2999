
# this is a stupid simple edit that works better
# creates output list of urls to try
def getUrl(rootUrl, wordListFile):
    wordList = open(wordListFile, encoding="utf8")
    outputUrl = open("outputUrlList.txt", "w+", encoding="utf8")
    l = wordList.readlines()
    for line in l:
        outputUrl.write(formatUrl(rootUrl, line))


def formatUrl(rootUrl, lineString):
    words = lineString.split(" ")
    newUrl = rootUrl
    isFirst = True
    for x in words:
        if isFirst:
            newUrl = newUrl + x.lower()
            isFirst = False
        else:
            newUrl = newUrl + "-" + x.lower()

    return newUrl


getUrl("https://www.pcmag.com/reviews/", "phoneListUnformatted.txt")





