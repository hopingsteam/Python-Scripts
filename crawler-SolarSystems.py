import requests
import csv
from robobrowser import RoboBrowser
from bs4 import BeautifulSoup

starting_url = 'https://www.enfsolar.com/directory/installer/other_europe?operating=229'
company_fields = ['name', 'url', 'address', 'phone', 'email', 'website', 'installation_size', 'ongrid',
                  'panel_suppliers', 'inverter_suppliers', 'company_parent']


def get_all_companies():
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

    browser = RoboBrowser(parser='html5lib', session=s)
    browser.open(starting_url)

    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, 'html5lib')

    all_companies_file = open('all_companies.txt', 'a')

    main_table = bsoup.find('table', {'class': 'enf-list-table'})
    company_rows = main_table.findAll('tr')
    for company_row in company_rows:
        row_url = company_row.find('a')
        if row_url is not None:
            company_url = row_url.attrs['href']
            directory = company_url.find('?')
            all_companies_file.write(company_url[:directory])
            all_companies_file.write('\n')

    all_companies_file.close()


def read_companies_url_file():
    all_companies_file = open('all_companies.txt', 'r')
    return all_companies_file.readlines()


def extract_company_info(company_url):
    company_email = 'not-set'
    company_phone = 'not-set'
    company_website = 'not-set'
    company_address = 'not-set'
    company_install_size = 'not-set'
    company_ongrid = 'not-set'
    company_panel_supplier = 'not-set'
    company_inverter_supplier = 'not-set'
    company_parent = 'not-set'

    print(f'Parsing url: {company_url}')
    s = requests.Session()
    s.headers['User-Agent'] = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:39.0) Gecko/20100101 Firefox/39.0'

    browser = RoboBrowser(parser='html5lib', session=s)
    browser.open(company_url)

    htmlpage = str(browser.parsed)
    bsoup = BeautifulSoup(htmlpage, 'html5lib')
    company_title = bsoup.find('h1', {'itemprop': 'name'}).text.strip()
    container_company_profile = bsoup.find('div', {'class': 'enf-company-profile-info-main-spec position-relative'})
    try:
        company_address = container_company_profile.find('td', {'itemprop': 'address'}).text.strip()
    except:
        company_address = 'not-set'
    try:
        company_phone = container_company_profile.find('td', {'itemprop': 'telephone'}).text.strip()
        if 'show company phone' in company_phone:
            company_phone = 'blocked'
    except:
        company_address = 'not-set'
    try:
        company_email = container_company_profile.find('td', {'itemprop': 'email'}).text.strip()
        if 'to get email' in company_email:
            company_email = 'blocked'
    except:
        company_address = 'not-set'
    try:
        company_website = container_company_profile.find('a', {'itemprop': 'url'}).attrs['href']
    except:
        company_address = 'not-set'

    container_company_installer = bsoup.find('div', {'id': 'installer'}) \
        .find('div', {'class': 'enf-section-body'}) \
        .findAll('div', {'class': 'enf-table-row'})
    if container_company_installer is not None:

        for installer_row in container_company_installer:
            attribute_name = installer_row.find('div', {'class': 'enf-section-body-title'}).text.strip()
            attribute_value = installer_row.find('div', {'class': 'enf-section-body-content'}).text.strip()
            if attribute_name == 'Installation size':
                company_install_size = attribute_value
            if attribute_name == 'On-Grid / Off-Grid':
                company_ongrid = attribute_value
            if attribute_name == 'Panel Suppliers':
                company_panel_supplier = attribute_value
            if attribute_name == 'Inverter Suppliers':
                company_inverter_supplier = attribute_value
            if attribute_name == 'Parent Company':
                company_parent = attribute_value

    company_data = {
        'name': company_title,
        'url': company_url,
        'address': company_address,
        'phone': company_phone,
        'website': company_website,
        'email': company_email,
        'installation_size': company_install_size,
        'ongrid': company_ongrid,
        'panel_suppliers': company_panel_supplier,
        'inverter_suppliers': company_inverter_supplier,
        'company_parent': company_parent
    }
    with open('enf_ro_companies.csv', mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=company_fields)
        writer.writerow(company_data)


def main():
    # get_all_companies()
    with open('enf_ro_companies.csv', mode='a') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=company_fields)
        writer.writeheader()

    for company_url in read_companies_url_file():
        extract_company_info(company_url.strip())


if __name__ == "__main__":
    main()
