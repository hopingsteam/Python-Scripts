import requests
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

judete = ["NULL", "AB", "AR", "AG", "BC", "BH", "BN", "BT", "BR", "BV", "B", "BZ", "CL", "CS", "CJ", "CT", "CV", "DB",
          "DJ", "GL", "GR", "GJ", "HR", "HD", "IL", "IS", "IF", "MM", "MH", "MS", "NT", "OT", "PH", "RM", "SJ", "SM",
          "SB", "SV", "TR", "TM", "TL", "VL", "VS", "VN"]

scoli = []

def getMaxPage(judet):
    URL = "http://static.bacalaureat.edu.ro/2018/rapoarte/" + judet + "/lista_unitati/page_1.html"
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

    browser = RoboBrowser(parser="html5lib", session=s)
    browser.open(URL)

    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, "html5lib")

    paginaMax = bsoup.findAll('option', {'class' : 'opte'})
    return paginaMax[-1].attrs['value']

def parcurgePagina(URL, judet):
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

    browser = RoboBrowser(parser="html5lib", session=s)
    browser.open(URL)

    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, "html5lib")

    tabel = bsoup.find('table', {'class': 'mainTable'})
    randuri = tabel.findAll('td', {'colspan': '4'})

    tabelLocalitate = bsoup.find('table', {'class': 'mainTable'})
    numeLocalitate = tabelLocalitate.findAll('td', {'class', 'td'})

    for rand in randuri:  # parcurgem randurile
        scoala = rand.text.strip()  # extragen doar numele scolii
        scoala2 = scoala.replace("\'","\"")
        scoli.append({"nume": scoala2, "judet": judete.index(judet)})

    tmp = len(scoli) - 10
    for i, randTabel in enumerate(numeLocalitate[1:]):
        if i % 3 != 0:
            continue
        scoli[tmp + int(i / 3)]["oras"] = randTabel.text.strip()

def printQuery():
    f = open("outputFile.txt", "a")
    for scoala in scoli:
        f.write("INSERT INTO `schools` (`id`, `name`, `county`, `location`, `created_at`, `updated_at`) VALUES (NULL, '" + scoala["nume"] + "', '" + str(scoala["judet"]) + "', '" + scoala["oras"] +"', NULL, NULL);")
        f.write("\n")

def main():
    for judet in judete[1:]:
        if judet is 'RM':
            continue
        maxPage = getMaxPage(judet)
        print("Parcurgem judetul " + judet + " (" + maxPage + " pagini totale)")

        for page in range(1, int(maxPage) + 1):
            linkURL = "http://static.bacalaureat.edu.ro/2018/rapoarte/" + judet + "/lista_unitati/page_" + str(page) + ".html"
            parcurgePagina(linkURL, judet)

        if judet is 'VN':
            break

    printQuery()

if __name__ == "__main__":
    main()