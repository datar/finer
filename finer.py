import urllib.request
import urllib.error
import datetime
import time
import os
import json
import requests
import lxml.html

import feed.china_market
#import Parsor.Futures

__author__ = 'gnix'
try_time = 10

RAW_DATA_DIR = '/Users/gnix/Code/finer/RawData'
TEST_DATA_DIR = '/Users/gnix/Code/finer/TestData'
JSON_DATA_DIR = '/Users/gnix/Code/finer/JSONData'
DEFAULT_HEADERS = {'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:83.0) Gecko/20100101 Firefox/83.0"}


def get_company_codes():
    lines = open('company_list.txt').readlines()
    company = dict()
    for line in lines:
        (company_code, company_name) = line.strip().split(',')
        company[company_code] = company_name
    return company.keys()


def get_company_people(company_code):
    page_url = feed.china_market.company_people_page_url_pattern % (company_code, )
    print('START::' + company_code)
    print('Fetching::' + page_url)
    page_content = ''
    for i in range(try_time):
        try:
            req = urllib.request.Request(page_url, headers=DEFAULT_HEADERS)
            page_content = urllib.request.urlopen(req, timeout=10).read()
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
    page_url = feed.china_market.ALL_PEOPLE_PAGE_URL
    req = urllib.request.Request(page_url, headers=DEFAULT_HEADERS)
    content = urllib.request.urlopen(req, timeout=30).read()
    out_file = open(filename, 'wb')
    out_file.write(content)
    out_file.close()
    return 1


def get_trunk_of_employee(current_page, page_size):
    request_url = feed.china_market.trunk_of_all_employee % (current_page, page_size)
    print(request_url, "\n")
    req = urllib.request.Request(request_url, headers=DEFAULT_HEADERS)
    page_content = urllib.request.urlopen(req, timeout=30).read()
    return page_content


def save_all_employee(date_str):
    output_file_pattern = "%s_all_employee_%06d_%06d.json"
    current_page = 1
    page_size = 500
    page_start = (current_page-1)*page_size+1
    while True:
        page_content = get_trunk_of_employee(current_page, page_size)
        result = json.loads(page_content.decode("utf-8"))
        if 'errcode' not in result:
            print(page_content)
            print('error_code missing\n')
            return

        if 'msg' not in result:
            print('msg is missing in result\n')
            return

        if 'data' not in result:
            print('data is missing in result\n')
            return

        data = result['data']
        if 'dataList' not in data:
            print('dataList is missing in result data')

        employee = data['dataList']
        total = data['total']
        result_size = len(employee)
        page_end = page_start + result_size - 1
        filename = output_file_pattern % (date_str, page_start, page_end)
        filepath = os.path.join(JSON_DATA_DIR, filename)
        out_file = open(filepath, 'wb')
        out_file.write(page_content)
        out_file.close()
        print("Saved: %s, %d-%d of %d\n" % (filename, page_start, page_end, total))
        if result_size < page_size:
            break
        page_start = page_start + result_size
        current_page += 1


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
    #save_all_data()
    save_all_employee('20210604')


if __name__ == '__main__':
    main()

