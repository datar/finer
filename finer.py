#import Parsor.Futures
import urllib.request
import urllib.error
import datetime
import time
import os
import requests
import lxml.html


__author__ = 'gnix'
company_people_page_url_pattern = 'http://www.cfachina.org/cfainfo/organbaseinfoOneServlet?organid=+%s+&currentPage=1&pageSize=2000&selectType=personinfo&all=undefined'
ALL_PEOPLE_PAGE_URL = 'http://www.cfachina.org/cfainfo/personinfoServlet?organid=&currentPage=1&pageSize=100000&selectType=check&cardid='
try_time = 5

RAW_DATA_DIR = 'RawData'
TEST_DATA_DIR = 'TestData'


def get_company_codes():
    lines = open('company_list.txt').readlines()
    company = dict()
    for line in lines:
        (company_code, company_name) = line.strip().split(',')
        company[company_code] = company_name
    return company.keys()


def get_company_people(company_code):
    page_url = company_people_page_url_pattern % (company_code, )
    print('START::' + company_code)
    print('Fetching::' + page_url)
    page_content = ''
    for i in range(try_time):
        try:
            page_content = urllib.request.urlopen(page_url).read()
            if len(page_content) < 1000:
                print('::'.join([company_code, 'try no.', str(i)]))
                time.sleep(6)
                continue
        except urllib.error.URLError as e:
            print(e.reason)
            print('::'.join([company_code, 'try no.', str(i)]))
            continue
        except urllib.error.HTTPError as e:
            # do something
            print('Error code: ', e.code)
            print('::'.join([company_code, 'try no.', str(i)]))
            continue
        break
    print('::'.join(['END', company_code, str(len(page_content))]))
    return page_content


def save_company_data(code):
    basename = "%s_%s.html" % (datetime.date.today().strftime('%Y%m%d'), code)
    filename = os.path.join(RAW_DATA_DIR, basename)
    if os.path.isfile(filename) and os.path.getsize(filename) > 1000:
        return
    content = get_company_people(code)
    out_file = open(filename, 'wb')
    out_file.write(content)
    out_file.close()


def save_all_people_in_one_page():
    basename = "%s_all_people.html" % (datetime.date.today().strftime('%Y%m%d'), )
    filename = os.path.join(TEST_DATA_DIR, basename)
    if os.path.isfile(filename) and os.path.getsize(filename) > 1000:
        return
    content = urllib.request.urlopen(ALL_PEOPLE_PAGE_URL).read()
    out_file = open(filename, 'wb')
    out_file.write(content)
    out_file.close()


def save_all_data():
    codes = get_company_codes()
    for code in codes:
        save_company_data(code)
    save_all_people_in_one_page()


def parse_company_page(page_text):
    page = lxml.html.fromstring(page_text)
    table_path = '//table/tr'
    rows = page.xpath(table_path)
    data = list()
    for row in rows:
        data.append([td.text.encode('utf-8') for td in row.getchildren()])
    return data


def test_parse():
    page_text = ''.join(open('RawData/20151109_G01001.html').readlines())
    info_table = parse_company_page(page_text)
    out_file = open('out_file.txt', 'wb')
    for line in info_table:
        out_file.write(','.join(line))
        out_file.write('\n')
    out_file.close()


def test():
    lines = open('company_list.txt', encoding='utf-8').readlines()
    company = dict()
    for line in lines:
        (company_code, company_name) = line.strip().split(',')
        company[company_code] = company_name
    print(company.values())


def main():
    save_all_data()


if __name__ == '__main__':
    main()

