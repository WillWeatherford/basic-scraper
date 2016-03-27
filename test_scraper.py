"""Test requsts and scraping facilities in scraper.py."""
import random
import pytest
import sys
from scraper import SORT_CHOICES

TEST_CONTENT = (b'<html><div>This is some nice HTML</div>'
                b'<p>Yep, HTML</p></html>')
TEST_FILE = 'write_test.txt'

ERROR_CASES = [
    ((b'<html><span>'
      b'Error: A database error occured when attempting to retrieve requested '
      b'data.</span></html>'), True),
    (b'<html><span>This is OK.</span></html>', False),
    (b'<html><span>Error: Something else...</span></html>', True)
]

UPDATE = [
    ('-u', True),
    ('--update', True),
    ('', False)
]

MAP = [
    ('-m', True),
    ('--map', True),
    ('', False)
]

REVERSE = [
    ('-r', True),
    ('--reverse', True),
    ('', False)
]
SORTBY = [(syntax.format(choice), choice)
          for choice in SORT_CHOICES
          for syntax in ['-s {}', '--sortby={}']]
SORTBY.append(('', 'average'))
NUMRESULTS = [(syntax.format(num), num)
              for num in random.sample(range(1, 10000), 5)
              for syntax in ['-n {}', '--numresults={}']]
NUMRESULTS.append(('', 99999999))


@pytest.fixture(params=UPDATE)
def update_param(request):
    """Establish a fixture for the -u --update console arg."""
    arg, result = request.param
    dic = {'update': result}
    return arg, dic


@pytest.fixture(params=MAP)
def map_param(request):
    """Establish a fixture for the -m --map update console arg."""
    arg, result = request.param
    dic = {'map': result}
    return arg, dic


@pytest.fixture(params=REVERSE)
def reverse_param(request):
    """Establish a fixture for the -r --reverse update console arg."""
    arg, result = request.param
    dic = {'reverse': result}
    return arg, dic


@pytest.fixture(params=SORTBY)
def sortby_param(request):
    """Establish a fixture for the -s --sortby update console arg."""
    arg, result = request.param
    dic = {'sortby': result}
    return arg, dic


@pytest.fixture(params=NUMRESULTS)
def numresults_param(request):
    """Establish a fixture for the -n numresults update console arg."""
    arg, result = request.param
    dic = {'numresults': result}
    return arg, dic


@pytest.fixture()
def params(update_param, reverse_param, map_param,
           sortby_param, numresults_param):
    """Establish a fixture of multiple params for the -u update console arg."""
    fixtures = [update_param, reverse_param, map_param,
                sortby_param, numresults_param]
    argv = []
    expected = {}
    for arg, param in fixtures:
        expected.update(param)
        if arg:
            argv.extend(arg.split())
    return argv, expected


def test_parse_args(params):
    """Test that args from the command line result in expected parameters."""
    argv, expected = params
    print(argv)
    print(expected)
    sys.argv = ['scraper.py'] + argv
    from scraper import parse_params
    assert parse_params() == expected


@pytest.fixture(scope='session')
def good_params():
    """Establish request params that should always work."""
    from scraper import PARAMS
    params = PARAMS.copy()
    params['Business_Name'] = 'CodeFellows'
    params['City'] = 'Seattle'
    return params


@pytest.mark.parametrize('html, expected', ERROR_CASES)
def test_has_error(html, expected):
    """Test that HTML with error message can be matched."""
    from scraper import has_error
    assert has_error(html) == expected


def test_wrong_type_param():
    """Test get_inspection_page raises error when given wrong parameters."""
    from scraper import get_inspection_page
    with pytest.raises(TypeError):
        get_inspection_page(Violation_Points=0, City='Seattle')


def test_missing_required_params():
    """Test get_inspection_page raises error when given wrong parameters."""
    from scraper import get_inspection_page
    with pytest.raises(TypeError):
        get_inspection_page(only_param='val')


def test_write_to_file():
    """Test that program can write to a file without raising an error."""
    from scraper import write_to_file
    encoding = 'utf-8'
    write_to_file(TEST_FILE, TEST_CONTENT, encoding)
    assert True


def test_read_from_file():
    """Test that we can read from a file without error."""
    from scraper import read_from_file
    assert read_from_file(TEST_FILE) == (TEST_CONTENT, 'utf-8')


def test_wrong_value_param():
    """Test get_inspection_page raises error when given wrong parameters."""
    from scraper import get_inspection_page
    with pytest.raises(ValueError):
        get_inspection_page(City='Seattle', bad_param='val')


def test_parse_file_source():
    """Test that BeautifulSoup object will be passed from HTML file."""
    from bs4 import BeautifulSoup
    from scraper import read_from_file, parse_source
    content, encoding = read_from_file(TEST_FILE)
    result = parse_source(content, encoding)
    assert isinstance(result, BeautifulSoup)


def test_calculate_color():
    """Test that color choice is correct."""
    from scraper import calculate_color, COLORS
    pass


# def test_parse_web_source(good_params):
#     from bs4 import BeautifulSoup
#     from scraper import get_inspection_page, parse_source
#     content, encoding = get_inspection_page(**good_params)
#     result = parse_source(content, encoding)
#     assert isinstance(result, BeautifulSoup)


# # test_db_error

# def test_get_inspection_page_response(good_params):
#     """Test that good request returns a 200 Response with bytes content."""
#     from scraper import get_inspection_page
#     content, encoding = get_inspection_page(**good_params)
#     assert isinstance(content, bytes) and encoding


# def test_main():
#     """Test main function reads and writes to file with default params."""
#     from scraper import main, read_from_file, INSPECTION_HTML_FILE
#     main()
#     results = read_from_file(INSPECTION_HTML_FILE)
#     assert results
