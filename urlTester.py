import requests, time


# open the file generated by urlFinder
# the line number corresponds to the index variable

def specificUrlTest(urlListFile, index):
    urlList = open(urlListFile, encoding="utf8")
    for i, line in enumerate(urlList):
        if i+1 == index:
            tryUrl = line.strip()
            print(tryUrl)
            response = requests.get(tryUrl)
            print(response)

specificUrlTest("outputUrlList.txt", 1522)
time.sleep(4)
specificUrlTest("outputUrlList.txt", 7)
time.sleep(4)
specificUrlTest("outputUrlList.txt", 991)
time.sleep(4)
specificUrlTest("outputUrlList.txt", 104)


# only test this using the test list
def allUrlTest(urlListFile):
    urlList = open(urlListFile, encoding="utf8")
    workingUrls = open("PCmagURLs.txt", "w+", encoding="utf8")
    for line in urlList:
        tryUrl = line.strip()
        response = requests.get(tryUrl)
        if response.status_code == 200:
            workingUrls.write(tryUrl)
        time.sleep(4)

allUrlTest("testUrlList.txt")







