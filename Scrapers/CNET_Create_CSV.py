import requests
import csv
from bs4 import BeautifulSoup
import time

#Search WebPage
#This method will grab the inital page so I can the use the html to get the total number of pages
def SearchWebPage():
    try:
        req = requests.get('https://www.cnet.com/topics/phones/products/')
        return req
    except Exception as e:
        print(f"Error\n{e}")


#Get Last Page
#Takes the initial web page and loks for the last page and returns the last page in the number of pages
def GetLastPageNumber(webPage):
    soup = BeautifulSoup(webPage, features="html.parser")
    lastNumberTag = soup.find("a", {"class":"page last"}).text
    return lastNumberTag

#Get all web pages
#returns the text from all the web pages combined, goes into a for loop and searches through all pages,
#with sleep for 10 seconds after grabbing all the text from each page
def GetAllWebPages(lastPageNumber):
    webText = ""
    pageNumber = 1
    for pageNumber in range(int(lastPageNumber) + 1):
        if(pageNumber == 1):
            try:
                req = requests.get('https://www.cnet.com/topics/phones/products/')
                webText = webText + req.text
                time.sleep(10)
            except Exception as e:
                print(f"Error\n{e}")
        else:
            try:
                req = requests.get('https://www.cnet.com/topics/phones/products/'+str(pageNumber))
                webText = webText + req.text
                time.sleep(10)
            except Exception as e:
                print(f"Error\n{e}")

    return webText

#Create CSV File
#takes the full web text from all the pages and searches for the correct identifier for the phone info, once it grabs
#the correct identifier it will then write into the csv file and only take the ones with review in the url
def CreateCSVFile(webPage):
    soup = BeautifulSoup(webPage, features="html.parser")
    phoneInfo = soup.find_all("div",{"class","itemInfo"})

    with open('CNET_Phone_Url.csv', 'wt', newline='') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',')
        for rows in phoneInfo:
            phoneName = rows.find('h3')
            phoneUrl = rows.find('a')
            if("reviews" in phoneUrl['href']):
                filewriter.writerow([phoneName.text.strip(), "www.cnet.com"+phoneUrl["href"]])

#Main
#Function that sets the steps the program needs to make
def Main():
    webPage = SearchWebPage()
    lastPageNumber = GetLastPageNumber(webPage.text)
    allWebPages = GetAllWebPages(lastPageNumber)
    CreateCSVFile(allWebPages)

Main()