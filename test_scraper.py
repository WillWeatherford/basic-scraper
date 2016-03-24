"""Test requsts and scraping facilities in scraper.py."""
import pytest

TEST_CONTENT = b'<html><div>This is some nice HTML</div><p>Yep, HTML</p></html>'
TEST_FILE = 'write_test.txt'


ERROR_CASES = [
    (('<html><span>'
      'Error: A database error occured when attempting to retrieve requested '
      'data.</span></html>'), True),
    ('<html><span>This is OK.</span></html>', False),
    ('<html><span>Error: Something else...</span></html>', True)
]


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
#     """Test that main function reads and writes to file with default params."""
#     from scraper import main, read_from_file, INSPECTION_HTML_FILE
#     main()
#     results = read_from_file(INSPECTION_HTML_FILE)
#     assert results
