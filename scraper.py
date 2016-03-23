"""Fetch data from kingcounty.gov using requests."""

import re
import requests
from bs4 import BeautifulSoup

DOMAIN = 'http://info.kingcounty.gov/'

SEARCH_PATH = (
    'health/ehs/foodsafety/inspections/Results.aspx?'
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


ERROR_PATTERN = r'Error: .*'


def get_inspection_page(**params):
    """Get search result page from health inspection site."""
    req_params = [p for p in REQUIRED_PARAMS if params.get(p, '')]
    if not req_params:
        raise TypeError(
            'At least one of these parameters is required: {}'
            ''.format(', '.join(REQUIRED_PARAMS))
        )
    try:
        param_list = ['='.join(pair) for pair in params.items()]
    except TypeError:
        raise TypeError(
            'All values to get_inspection_page parameters must be strings.'
        )

    root_url = ''.join([DOMAIN, SEARCH_PATH])
    param_string = '&'.join(param_list)
    final_search_url = '?'.join([root_url, param_string])

    response = requests.get(final_search_url)
    if has_error(response.text):
        raise requests.RequestException('kingcounty.gov database error.')
    return response.content, response.encoding


def has_error(u_content):
    """Search HTML content to determin if content contains an error message."""
    soup = BeautifulSoup(u_content)
    return bool(soup.find(string=re.compile(ERROR_PATTERN)))


def write_to_file(filename, b_content, encoding='utf-8'):
    """Write bytes content to given filename, with given encoding."""
    with open(filename, 'w') as fh:
        u_content = b_content.decode(encoding)
        fh.write(u_content)
