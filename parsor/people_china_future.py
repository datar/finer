import lxml.html


def get_people(page):
	document = lxml.html.fromstring(page)
	table = []
	for row in document.xpath('//table/tr'):
		table.append([td.text for td in row])
	return tabl