import lxml.html


def get_people_from_page(page):
	document = lxml.html.fromstring(page)
	table = []
	for row in document.xpath('//table/tr'):
		table.append([td.text for td in row])
	if len(table) > 0:
		return table[1:]
	else:
		return table


def get_info_from_filename(filename):
	date_str = filename[0:8]
	company_code = filename[11:15]
	return date_str, company_code


def get_people_from_file(filename):
	date_str, company_code = get_info_from_filename(filename)
	with open(filename) as infile:
		page = infile.read()
		content = get_people_from_page(page)
	infile.close()
	return date_str, company_code, content


def normalize_people_daily_info(date_str, company_code, page):
	n = [x.extend([date_str, company_code]) for x in page]
	return n