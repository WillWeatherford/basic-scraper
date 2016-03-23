"""Test requsts and scraping facilities in scraper.py."""
import pytest

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
    params['City'] = 'CodeFellows'
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
    filename = 'write_test.txt'
    bytes_content = b'This is some bytes of text.'
    encoding = 'utf-8'
    write_to_file(filename, bytes_content, encoding)
    assert True


# def test_wrong_value_param():
#     """Test get_inspection_page raises error when given wrong parameters."""
#     from scraper import get_inspection_page
#     with pytest.raises(requests.RequestException):
#         get_inspection_page(City='Seattle', bad_param='val')


# def test_get_inspection_page_response(good_params):
#     """Test that good request returns a 200 Response with bytes content."""
#     from scraper import get_inspection_page
#     content, encoding = get_inspection_page(**good_params)
#     assert isinstance(content, bytes) and encoding
