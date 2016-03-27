"""Fetch data from kingcounty.gov using requests."""

import re
import json
import pprint
import argparse
import geocoder
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

USABLE_RESULT_PARAMS = [
    'Business Name',
    'Number of Inspections',
    'Highest Inspection Score',
    'Average Inspection Score',
    'marker-color',
]

SORT_CHOICES = {
    'count': 'Number of Inspections',
    'highest': 'Highest Inspection Score',
    'average': 'Average Inspection Score',
}

COLORS = ['CC0000', 'CC33000', 'CC6600', 'CC9900', 'CCCC00', 'CCFF00']


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
    content, encoding = response.content, response.encoding
    response.raise_for_status()
    if has_error(content, encoding):
        raise requests.RequestException('kingcounty.gov database error.')

    return content, encoding


def has_error(content, encoding='utf-8'):
    """Search HTML content to determine if content contains error message."""
    soup = BeautifulSoup(content, 'html5lib', from_encoding=encoding)
    return bool(soup.find(string=re.compile(ERROR_PATTERN)))


def write_to_file(filename, b_content, encoding='utf-8'):
    """Write bytes content to given filename, with given encoding."""
    with open(filename, 'wb') as fh:
        fh.write(b_content)


def read_from_file(filename):
    """Read unicode from given filename."""
    with open(filename, 'rb') as fh:
        text = fh.read()
        return text, 'utf-8'


def parse_source(content, encoding='utf-8'):
    """Return a BeautifulSoup object from provided content."""
    return BeautifulSoup(content, 'html5lib', from_encoding=encoding)


def extract_data_listings(soup):
    """Extract data listing divs which end with tilde."""
    container = soup.find('table', id='container')
    return container.find_all('div', id=lambda t: t.endswith('~'))


def has_two_tds(tag):
    """Check if an tag is a table row with two cells."""
    return all((tag.name == 'tr',
                len(tag.find_all('td', recursive=False)) == 2,
                not tag.find('table')))


def clean_data(tag):
    """Return only the string of given tag."""
    try:
        return tag.string.strip(' \n:-')
    except AttributeError:
        return ''


def calculate_color(idx, segment, value):
    """Calculate the color for listing at index, relative to the best."""
    color_idx = int(value // segment)
    return COLORS[min(color_idx, len(COLORS) - 1)]


def extract_restaurant_data(listing):
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

    insp_rows = listing.find_all(is_ispection_row)
    scores = [int(clean_data(list(row.children)[2])) for row in insp_rows]
    num_scores = len(scores)
    if scores:
        highest = max(scores)
        avg = float('{0:.2f}'.format(sum(scores) / float(num_scores)))
    else:
        highest, avg = 0, 0.0
    data['Number of Inspections'] = num_scores
    data['Highest Inspection Score'] = highest
    data['Average Inspection Score'] = avg
    return data


def is_ispection_row(tag):
    """Determine if a tag is table row with inspection score data."""
    cells = tag.find_all('td', recursive=False)
    return tag.name == 'tr' and\
        len(cells) == 4 and\
        'Inspection' in (cells[0].string or '') and\
        (cells[2].string or '').isdigit()


def get_geojson(insp_data):
    """Return geoJSON data from the address of a given inspection result."""
    address = insp_data.get('Address')
    if not address:
        return {}
    insp_data = {key: insp_data[key] for key in USABLE_RESULT_PARAMS}
    geojson = geocoder.google(address).geojson
    prop = geojson['properties']
    new_address = prop.get('address', prop.get('location', ''))
    if new_address:
        insp_data['Address'] = new_address
    geojson['properties'] = insp_data
    return geojson


def generate_results(update=False, **params):
    """Generate dictionaries of inspection data results."""
    if update:
        final_params = DEFAULT_PARAMS.copy()
        final_params.update(params)
        content, encoding = get_inspection_page(**final_params)
        write_to_file(INSPECTION_HTML_FILE, content, encoding)
    else:
        content, encoding = read_from_file(INSPECTION_HTML_FILE)

    soup = parse_source(content, encoding)
    listings = extract_data_listings(soup)
    return [extract_restaurant_data(listing) for listing in listings]


def main(sortby='average', reverse=True, numresults=99999999, **params):
    """Main function to run from command line."""
    collection = {'type': 'FeatureCollection', 'features': []}
    results = generate_results(**params)

    sortby = SORT_CHOICES[sortby]
    results.sort(key=lambda d: d[sortby], reverse=reverse)

    largest = results[reverse - 1][sortby]  # clever trick to find largest.
    segment = largest / len(COLORS)

    for idx, result in enumerate(results[:numresults]):
        result['marker-color'] = calculate_color(idx, segment, result[sortby])
        geojson = get_geojson(result)
        collection['features'].append(geojson)
        pprint.pprint(geojson)

    with open('inspection_map.json', 'w') as fh:
        json.dump(collection, fh)


def parse_params():
    """Use argparse module to return parsed params for scraping."""
    parser = argparse.ArgumentParser(
        description='Display data on kingcounty.goc health inspections.')
    parser.add_argument('-u', '--update', action='store_true',
                        help='Make web request to kingcounty.gov to'
                        'get latest data.')
    parser.add_argument('-n', '--numresults', type=int, default=99999999,
                        help='Number of rows to display.')
    parser.add_argument('-s', '--sortby', type=str, default='average',
                        choices=SORT_CHOICES,
                        help='Select a column on which to sort data.')
    parser.add_argument('-r', '--reverse', action='store_false',
                        help='Sort data in reverse order.')
    parser.add_argument('-m', '--map', action='store_true',
                        help='Sort data in reverse order.')

    params = parser.parse_args()
    return vars(params)


if __name__ == '__main__':
    params = parse_params()
    main(**params)
