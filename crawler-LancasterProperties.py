# Fiver order no. FO511DEA1DA66
# Buyer: #
# Author: Mihai-Alexandru Matraguna

import tabula
import re
import os
import requests
import lxml.html as lh
import time
from PyPDF2 import PdfFileReader
from io import StringIO
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup
import pandas as pd
from pandas import read_json, read_csv
from datetime import datetime

rxcountpages = re.compile(r"/Type\s*/Page([^s]|$)", re.MULTILINE|re.DOTALL)

def count_pages(filename):
    with open(filename, 'rb') as f:
        pdf = PdfFileReader(f)
        return pdf.getNumPages()

def convertPDF(propertyID, propertyNumber):
    print("[Crawler INFO]: Property #" + str(propertyID) + " - Converting the PDF into CSVs")
    pdfFile = "PDFs/property_" + str(propertyID) + ".pdf"
    pages = count_pages(pdfFile)
    df_page1 = tabula.read_pdf(pdfFile, pages='1', multiple_tables=True, area=  [[19.305,21.285,131.175,219.285],
                                                                                [39.105,223.245,132.165,787.545],
                                                                                [134.145,19.305,171.765,216.315],
                                                                                [134.145,219.285,205.425,778.635],
                                                                                [173.745,22.275,326.205,214.335],
                                                                                [207.405,222.255,279.675,772.695],
                                                                                [281.655,224.235,439.065,496.485],
                                                                                [281.655,498.465,444.015,775.665],
                                                                                [327.195,17.325,419.265,213.345],
                                                                                [445.995,215.325,491.535,778.635]])

    folderPath = "CSVs/" + propertyNumber
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)
    df_page1[0].to_csv("CSVs/" + propertyNumber + "/OWNER NAME AND MAILING ADDRESS.csv",  header=False, index=False)
    df_page1[1].to_csv("CSVs/" + propertyNumber + "/SALES INFORMATION.csv",               header=False, index=False)
    df_page1[2].to_csv("CSVs/" + propertyNumber + "/PROPERTY SITUS ADDRESS.csv",          header=False, index=False)
    df_page1[3].to_csv("CSVs/" + propertyNumber + "/BUILDING PERMITS.csv",                header=False, index=False)
    df_page1[4].to_csv("CSVs/" + propertyNumber + "/GENERAL PROPERTY INFORMATION.csv",    header=False, index=False)
    df_page1[5].to_csv("CSVs/" + propertyNumber + "/INSPECTION HISTORY.csv",              header=False, index=False)
    df_page1[6].to_csv("CSVs/" + propertyNumber + "/RECENT APPEAL HISTORY.csv",           header=False, index=False)
    df_page1[7].to_csv("CSVs/" + propertyNumber + "/ASSESSED VALUE HISTORY.csv",          header=False, index=False)
    df_page1[8].to_csv("CSVs/" + propertyNumber + "/PROPERTY FACTORS.csv",                header=False, index=False)
    df_page1[9].to_csv("CSVs/" + propertyNumber + "/MARKET LAND INFORMATION.csv",         header=False, index=False)

    if pages == 2:
        df_page2 = tabula.read_pdf(pdfFile, pages='2', multiple_tables=True, area=[[142.065, 25.245, 194.535, 216.315],
                                                                                   [196.515, 24.255, 302.445, 215.325],
                                                                                   [304.425, 23.265, 368.775, 214.335],
                                                                                   [365.805, 270.765, 420.255, 781.605],
                                                                                   [370.755, 21.285, 423.225, 262.845],
                                                                                   [424.215, 24.255, 577.665, 414.315],
                                                                                   [424.215, 415.305, 592.515,
                                                                                    781.605]])
        df_page2[0].to_csv("CSVs/" + propertyNumber + "/RESIDENTIAL SECTIONS.csv",            header=False, index=False)
        df_page2[1].to_csv("CSVs/" + propertyNumber + "/RESIDENTIAL INFORMATION.csv",         header=False, index=False)
        df_page2[2].to_csv("CSVs/" + propertyNumber + "/DWELLING COST SUMMARY.csv",           header=False, index=False)
        df_page2[3].to_csv("CSVs/" + propertyNumber + "/BUILDING COMMENTS.csv",               header=False, index=False)
        df_page2[4].to_csv("CSVs/" + propertyNumber + "/INCOME INFORMATION.csv",              header=False, index=False)
        df_page2[5].to_csv("CSVs/" + propertyNumber + "/RESIDENTIAL COMPONENTS.csv",          header=False, index=False)
        df_page2[6].to_csv("CSVs/" + propertyNumber + "/RESIDENTIAL COMPONENTS_2.csv",        header=False, index=False)

def downloadPDF(url, propertyID, propertyNumber):
    print("[Crawler INFO]: Property #" + str(propertyID) + " - Downloading PDF")

    browser = RoboBrowser(parser="html5lib")
    pdf_file_path = "PDFs/property_" + str(propertyID) + ".pdf"
    request = browser.session.get(url, stream=True)
    content = request.content

    folderPath = "PDFs"
    if not os.path.exists(folderPath):
        os.mkdir(folderPath)

    if b"Error occured" in content:
        print("[Crawler ERROR]: Could not download PDF from property #" + str(propertyID))
    else:
        with open(pdf_file_path, "wb") as pdf_file:
            pdf_file.write(content)
        convertPDF(propertyID, propertyNumber)

def urlParser(propertyID):
    print("[Crawler INFO]: Property #" + str(propertyID) + " - Opening URL page")
    downloadURL = "http://orion.lancaster.ne.gov/Appraisal/PublicAccess/PropertyDataSheet.aspx?PropertyID=" + str(propertyID) + "&PropertyOwnerID=230918&NodeID=11"

    propertyPage = "http://orion.lancaster.ne.gov/Appraisal/PublicAccess/PropertyDetail.aspx?PropertyID=" + str(propertyID)

    browser = RoboBrowser(parser="html5lib")
    browser.open(propertyPage)
    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, "html5lib")

    pattern = re.compile(r"var ParcelIDValue = \"(.*?)\";$", re.MULTILINE | re.DOTALL)
    script = bsoup.find("script", text=pattern)
    propertyNumber = pattern.search(script.text).group(1)

    treasurePage = "https://www.lincoln.ne.gov/aspx/cnty/cto/property.aspx?vParcel=" + str(propertyNumber)

    downloadPDF(downloadURL, propertyID, propertyNumber)
    downloadTreasureInfo(treasurePage, propertyID, propertyNumber)
    print("[Crawler INFO]: Property #" + str(propertyID) + " - COMPLETE!!")

def processTable(tableString, columns):
    doc = lh.fromstring(tableString)
    tr_elements = doc.xpath('//tr')
    col = []
    i = 0
    for t in tr_elements[0]:
        i += 1
        name = t.text_content()
        #print(str(i) + " " + name)
        col.append((name, []))
    for j in range(0, len(tr_elements)):
        T = tr_elements[j]
        if len(T) != columns:
            break
        i = 0

        for t in T.iterchildren():
            data = t.text_content()
            if i > 0:
                try:
                    data = int(data)
                except:
                    pass
            col[i][1].append(data)
            i += 1
    Dict = {title: column for (title, column) in col}
    return pd.DataFrame(Dict)

def downloadTreasureInfo(url, propertyID, propertyNumber):
    print("[Crawler INFO]: Downloading treasure info for property #" + str(propertyID))

    browser = RoboBrowser(parser="html5lib")
    browser.open(url)
    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, "html5lib")

    tablePropertyPayment = bsoup.find("table", {'class' : 'tableData gvPay tabRespon'})
    tablePropertyTax = bsoup.find("table", {'class': 'tableData gvHist tabRespon'})
    strTablePropertyTax = str(tablePropertyTax)
    strtablePropertyPayment = str(tablePropertyPayment)

    try:
        dataFramePropertyTax = processTable(strTablePropertyTax, 9)
        dataFramePropertyTax.to_csv("CSVs/" + propertyNumber + "/TREASURE INFO -  Property Tax History.csv",  header=False, index=False)
    except:
        print("[Crawler ERROR]: Could not find Property Tax History for property #"  + str(propertyID))
    try:
        dataFramePropertyPayment = processTable(strtablePropertyPayment, 13)
        dataFramePropertyPayment.to_csv("CSVs/" + propertyNumber + "/TREASURE INFO -  Property Payment.csv",  header=False, index=False)
    except:
        print("[Crawler ERROR]: Could not find Property Payment for property #"  + str(propertyID))

def main():
    print("[Crawler INFO]: PROCESS START")
    minPropertyID = input("Input the start ID: ") #70194
    maxPropertyID = input("Input the stop ID: ") #70200
    for i in range(int(minPropertyID),int(maxPropertyID)):
        propertyID = i
        urlParser(propertyID)

        time.sleep(1)
        print("[Crawler INFO]: ((SLEEPING 1 SECOND ))")
        #time.sleep(0.5) sleep for half a second

    print("[Crawler INFO]: PROCESS STOP!")
if __name__== "__main__":
  main()
