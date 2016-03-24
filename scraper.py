"""Fetch data from kingcounty.gov using requests."""

import re
import sys
import requests
from bs4 import BeautifulSoup

DOMAIN = 'http://info.kingcounty.gov'

SEARCH_PATH = (
    '/health/ehs/foodsafety/inspections/Results.aspx'
)

REQUIRED_PARAMS = ['Business_Name', 'Business_Address', 'City', 'Zip_Code']
PARAMS = dict(
    Output='W',
    Business_Name='',
    Business_Address='',
    Longitude='',
    Latitude='',
    City='',
    Zip_Code='',
    Inspection_Type='All',
    Inspection_Start='',
    Inspection_End='',
    Inspection_Closed_Business='A',
    Violation_Points='',
    Violation_Red_Points='',
    Violation_Descr='',
    Fuzzy_Search='N',
    Sort='H'
)
DEFAULT_PARAMS = PARAMS.copy()
DEFAULT_PARAMS.update(dict(
    Zip_Code='98107',
    Inspection_Start='1/1/2015',
    Inspection_End='12/31/2015',
))

ERROR_PATTERN = r'Error: .*'

INSPECTION_HTML_FILE = 'inspection_page.html'


def main(command='normal', **params):
    """Main function to run from command line."""

    if command == 'normal':
        final_params = DEFAULT_PARAMS.copy()
        final_params.update(params)
        content, encoding = get_inspection_page(**final_params)
        write_to_file(INSPECTION_HTML_FILE, content, encoding)
    elif command == 'test':
        content, encoding = read_from_file(INSPECTION_HTML_FILE)

    soup = parse_source(content, encoding)
    listings = extract_data_listings(soup)
    # print(len(listings))
    # print(listings[0].prettify())
    for listing in listings[:5]:
        print(extract_restaurant_metadata(listing))
        print('\n')


def get_inspection_page(**params):
    """Get search result page from health inspection site."""
    req_params = [p for p in REQUIRED_PARAMS if params.get(p, '')]
    if not req_params:
        raise TypeError(
            'At least one of these parameters is required: {}'
            ''.format(', '.join(REQUIRED_PARAMS))
        )

    for key, val in params.items():
        if not isinstance(val, str):
            raise TypeError(
                'Value for parameter "{}" must be a string.'.format(key))
        if key not in PARAMS:
            raise ValueError('"{}" is not a valid parameter.'.format(key))

    root_url = ''.join([DOMAIN, SEARCH_PATH])
    response = requests.get(root_url, params=params)
    if has_error(response.text):
        raise requests.RequestException('kingcounty.gov database error.')
    response.raise_for_status()
    return response.content, response.encoding


def has_error(u_content):
    """Search HTML content to determine if content contains an error message."""
    soup = BeautifulSoup(u_content)
    return bool(soup.find(string=re.compile(ERROR_PATTERN)))


def write_to_file(filename, b_content, encoding='utf-8'):
    """Write bytes content to given filename, with given encoding."""
    with open(filename, 'wb') as fh:
        fh.write(b_content)


def read_from_file(filename):
    """Read unicode from given filename."""
    with open(filename, 'rb') as fh:
        text = fh.read()
        # use chardet to guess encoding
        return text, 'utf-8'


def parse_source(content, encoding='utf-8'):
    """Return a BeautifulSoup object from provided content."""
    return BeautifulSoup(content, 'html5lib', from_encoding=encoding)


def extract_data_listings(soup):
    """Extract data listing divs which end with tilde."""
    main_table = soup.find('table', id='container')
    return main_table.find_all('div', id=lambda t: t.endswith('~'))


def has_two_tds(tag):
    """Check if an tag is a table row with two cells."""
    return all((tag.name == 'tr',
                len(tag.find_all('td', recursive=False)) == 2,
                not tag.find('table')))


def clean_data(tag):
    """Returns only the string of given tag."""
    try:
        return tag.string.strip(' \n:-')
    except AttributeError:
        return ''


def extract_restaurant_metadata(listing):
    """Return a dictionary of the listing information for the restaurant."""
    data = {}
    meta_table = listing.find('tbody')
    rows = meta_table.find_all(has_two_tds, recursive=False)
    prev_param = ''
    prev_value = ''
    for row in rows:
        param, value = [clean_data(tag) for tag in row.find_all('td')]
        if param:
            prev_param = param
            prev_value = value
        else:
            param = prev_param
            value = ' '.join([prev_value, value])
        data[param] = value
    return data

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        command = 'normal'
    elif args[0] == 'test':
        command = 'test'
    main(command=command)
