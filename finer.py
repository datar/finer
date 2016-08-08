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
try_time = 10

RAW_DATA_DIR = '/home/ec2-user/finer/RawData'
TEST_DATA_DIR = '/home/ec2-user/finer/TestData'


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
            page_content = urllib.request.urlopen(page_url, timeout=10).read()
            if len(page_content) < 1000:
                print('::'.join([company_code, 'try no.', str(i)]))
                time.sleep(6)
                continue
        except urllib.error.URLError as e:
            print(e.reason)
            print('::'.join([company_code, 'try no.', str(i)]))
            continue
        except urllib.error.HTTPError as e:
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
        return 0
    content = get_company_people(code)
    if len(content) > 1000:
        out_file = open(filename, 'wb')
        out_file.write(content)
        out_file.close()
        return 1
    else:
        return 0


def save_all_people_in_one_page():
    basename = "%s_all_people.html" % (datetime.date.today().strftime('%Y%m%d'), )
    filename = os.path.join(TEST_DATA_DIR, basename)
    if os.path.isfile(filename) and os.path.getsize(filename) > 1000:
        return 0
    content = urllib.request.urlopen(ALL_PEOPLE_PAGE_URL, timeout=10).read()
    out_file = open(filename, 'wb')
    out_file.write(content)
    out_file.close()
    return 1


def save_all_data():
    codes = get_company_codes()
    fail_list = list()
    for code in codes:
        if save_company_data(code) == 0:
            fail_list.append(code)
    print("TOTAL SAVE %d FILES, FAILED %d" % (len(codes)-len(fail_list), len(fail_list)))
    if save_all_people_in_one_page():
        print("SAVED ALL PEOPLE IN ONE PAGE")
    else:
        print("NOT SAVE PEOPLE IN ONE PAGE")


def main():
    save_all_data()


if __name__ == '__main__':
    main()

