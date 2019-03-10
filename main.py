# Fiver order no. FO513007E3BC7
# Buyer: #
# Author: Mihai-Alexandru Matraguna

import sqlite3
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup
from datetime import datetime

sqlConnection = sqlite3.connect('database.db')

outputFile = open("outputFile.txt", "a+")

def checkTitle(itemTitle):
    sql = sqlConnection.cursor()

    sqlString = "SELECT * FROM items WHERE title = ?"
    sql.execute(sqlString,(itemTitle,))
    result = sql.fetchone()
    if result is None:
        return False

    return True

def urlParser(url):
    browser = RoboBrowser(parser="html5lib")
    browser.open(url)

    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, "html5lib")
    return bsoup

def writeInfo(infoTitle, infoDescription, infoSource):
    outputFile.write("*" + infoTitle + "*\n")
    outputFile.write(infoDescription + " - Source: " + infoSource + "\n\n")
    infoDate = datetime.date(datetime.now());

    sql = sqlConnection.cursor()
    sqlString = "INSERT INTO items (title, description, source, itemDate) VALUES (?,?,?,?)"
    sql.execute(sqlString,(infoTitle,infoDescription,infoSource,infoDate))
    sqlConnection.commit()

def printResult(inserted, rejected, source):
    print("[INFO]: " + str(inserted) + " inserted rows")
    print("[INFO]: " + str(rejected) + " duplicates found")
    print("[SUCCESS]: " + source + " crawled succesfully.")

def getURL(option):
    if option == 1:
        return "http://feeds.bbci.co.uk/sport/football/rss.xml"
    if option == 2:
        return "http://feeds.bbci.co.uk/sport/football/rss.xml"
    if option == 3:
        return "https://www.kingfut.com/feed/"
    else:
        return "None"

def processTitle(option, item):
    if option == 1:
        return str(item.find("title"))[19:-14]
    if option == 2:
        return str(item.find("title"))[19:-14]
    if option == 3:
        return str(item.find("title"))[7:-8]
    else:
        return "None"

def processDescription(option, item):
    if option == 1:
        return str(item.find("description"))[24:-19]
    if option == 2:
        return str(item.find("description"))[24:-19]
    if option == 3:
        rawString = str(item.find("description"))[29:-25]
        cleanText = BeautifulSoup(rawString, "lxml").text
        return cleanText
    else:
        return "None"

def processSource(option):
    if option == 1:
        return "bbc.co.uk"
    if option == 2:
        return "kingfut.com"
    if option == 3:
        return "goal.com"
    else:
        return "None"

def parser(option):
    bsoup = urlParser(getURL(option))

    itemsInserted = 0
    itemsRejected = 0
    for item in bsoup.find_all('item'):
        item_title = processTitle(option, item)
        item_description = processDescription(option, item)
        item_source = processSource(option)
        if (checkTitle(item_title) == False):
            writeInfo(item_title, item_description, item_source)
            itemsInserted += 1
        else:
            itemsRejected += 1

    printResult(itemsInserted, itemsRejected, item_source)

def main():
    sql = sqlConnection.cursor()
    sql.execute('''CREATE TABLE IF NOT EXISTS items (title text, description text, source text, itemDate date)''')

    print("Please input your RSS: ")
    print("[ 1 ] - feeds.bbci.co.uk ")
    print("[ 2 ] - kingfut.com ")
    print("[ 3 ] - goal.com ")

    option = int(input("Please input your option: "))

    parser(option)

if __name__== "__main__":
  main()
