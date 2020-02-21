import requests
from bs4 import BeautifulSoup

# returns float representing score out of ten
# really just relied on strings rather than html elements but it gets the job done
# for pages that review multiple phones, wired gives all phones the same score
def getWiredReviewScore(reviewPageUrl):
    reviewPage = requests.get(reviewPageUrl)
    soup = BeautifulSoup(reviewPage.content, "html.parser")
    el = soup.find_all("li")
    for x in el:
        if "Rate" in x.text:
            scoreOutOfTen = float(x.text[4])
            break

    return scoreOutOfTen


#test
print(getWiredReviewScore("https://www.wired.com/2016/11/review-meizu-m3-note/"))


