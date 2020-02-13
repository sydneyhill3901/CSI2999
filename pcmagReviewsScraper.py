import requests
from bs4 import BeautifulSoup


# returns float representing score scaled to be out of ten
# pcmag does not give scores for multiple phones in one review page
def getPCmagReviewScore(reviewPageUrl):
    reviewPage = requests.get(reviewPageUrl)
    soup = BeautifulSoup(reviewPage.content, "html.parser")
    x = soup.find("div", class_="flex flow-row justify-center content-center mr-2")
    scoreOutOfTen = float(x.text.strip())*2

    return scoreOutOfTen


#test
print(getPCmagReviewScore("https://www.pcmag.com/reviews/samsung-galaxy-s10"))
