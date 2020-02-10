import requests


#the following opens the unformatted cell phone list to create bruteforce wordlist
fList = open("phoneListUnformatted.txt", encoding="utf8")  #long list

# not sure how to create empty string lists so heres garbage
wordList = ["phone"]
urlShortTry = ["cat"]

sList = open("phoneShortList.txt", encoding="utf8")  #short list for testing
shTryList = open("shTryList.txt", "a+", encoding="utf8")  #urls written here

#to run short list text, comment out "for x in fList" ; uncomment "for x in sList"
#i dont reccomend allowing the long list program to run completely
#for x in fList:
for x in sList:
        lineList = x.strip().split(' ')
        wordList.extend(lineList)

#remove duplicates in list
wordDict = dict.fromkeys(wordList)
wordList = list(wordDict)
print(wordList)

# writes long list to another file, without duplicates
nList = open("capWordList.txt", "w+", encoding="utf8")
for x in wordList:
    nList.write(x)

# 5 places to format
url = "https://www.pcmag.com/reviews/{0}{1}{2}{3}{4}"

# if we wanted to add index numbers to lists
indexIncrement = 0

for x in wordList:
    brand = x.lower()+"-"
    for x in wordList:
        line = x.lower()+"-"
        for x in wordList:
            num = x.lower()
            shTryUrl = url.format(brand, line, "", num, "")
            indexIncrement += 1
            # verify output, append to list, write to file

            print(shTryUrl+ "   ")                   #uncomment for long list try to verify
            urlShortTry.append(shTryUrl)            #uncomment for short list try to create list
            shTryList.write(shTryUrl+"\n")          #uncomment for short list try to write file



#bruteforce try, individual urls only at this point
# 850 , 4531  corresponds to line numbers in text file output
def specificTry(index):

    testUrl = urlShortTry[index]
    response = requests.get(testUrl)
    if response == "<Response [404]>":
        print("not a valid link")   #not working so we see 404
    else :
        print(response)



specificTry(850)
specificTry(4531)
specificTry(87)

