import pytest
from chatInsights import (
    _fetchDateAndTime,
    _findAuthor,
    _fetchMessages,
    _transformData,
)


good_data1 = [
    ("03/11/22, 2:03 pm - +91 54875 94258: Any Android ios dev here?", True),
    ("03/11/22, 2:03 pm - +91 74748 94258: @919003135354", True),
    (
        "03/11/22, 5:20 pm - +91 98956 82524: BigCode releases The Stack: the largest code dataset (like GitHub Copilot)",
        True,
    ),
]

bad_data1 = [
    ("03/11/2022, 2:03 pm - +91 85459 94258: Any Android ios dev here?", False),
    ("03/11/22 2:03 pm - +91 58965 94258: @919003135354", False),
    (
        "03/11/22, 5:20 PM - +91 22222 82524: BigCode releases The Stack: the largest code dataset (like GitHub Copilot)",
        False,
    ),
]


@pytest.mark.parametrize("input, expected", good_data1)
def test_fetchDateAndTime_good(input, expected):
    assert bool(_fetchDateAndTime(input)) == expected


@pytest.mark.parametrize("input, expected", bad_data1)
def test_fetchDateAndTime_bad(input, expected):
    assert bool(_fetchDateAndTime(input)) == expected


good_data2 = [
    ("ronilpatil: Any Android ios dev here?", True),
    ("ronil patil: Any Android ios dev here?", True),
    ("ronil patil python package developer: Any Android ios dev here?", True),
    ("ronil patil 🦉🦉🦉: Any Android ios dev here?", True),
    ("+1 (205) 692-6663: Any Android ios dev here?", True),
    ("+91 54856 94258: Any Android ios dev here?", True),
    ("+56 265 245 1255: Any Android ios dev here?", True),
    ("+234 999 631 1539: Any Android ios dev here?", True),
    ("+597 57 421 6849: Any Android ios dev here?", True),
    ("+21 8889 254168: Any Android ios dev here?", True),
    ("+34 543 678 231: Any Android ios dev here?", True),
    ("+65 8454 7719: Any Android ios dev here?", True),
    ("+91 6370 376 940: Any Android ios dev here?", True),
    ("+55 11 99224-4030: Any Android ios dev here?", True),
    ("+91 73688 94258: Any Android ios dev here?", True),
    ("🦉🦉🦉: Any Android ios dev here?", True),
]

bad_data2 = [
    ("+1 2056926663: Any Android ios dev here?", False),
    ("+91 54856 94258 45874: Any Android ios dev here?", False),
    ("+56 265 2451255: Any Android ios dev here?", False),
    ("+234999 631 1539: Any Android ios dev here?", False),
    ("+34 54378 231: Any Android ios dev here?", False),
    ("-65 8454 7719: Any Android ios dev here?", False),
    ("-91 6370 376 940: Any Android ios dev here?", False),
    ("+55-11-99224-4030: Any Android ios dev here?", False),
    ("+91 (73688) (94258): Any Android ios dev here?", False),
]


@pytest.mark.parametrize("input, expected", good_data2)
def test_findAuthor_good(input, expected):
    assert bool(_findAuthor(input)) == expected


@pytest.mark.parametrize("input, expected", bad_data2)
def test_findAuthor_bad(input, expected):
    assert bool(_findAuthor(input)) == expected


good_data3 = [
    ("03/11/22, 2:03 pm - +91 54875 45875: Any Android ios dev here?"),
    ("03/11/22, 2:03 pm - +91 45888 94258: @919003135354"),
    ("03/11/22, 5:27 pm - +234 555 631 1539: yeah, running it with sudo produces that"),
    (
        "03/11/22, 5:20 pm - +91 88888 82524: BigCode releases The Stack: the largest code dataset (like GitHub Copilot)\
         BigCode is a 3TB dataset of permissively licensed code scraped from GitHub, including 30 languages."
    ),
]


def is_valid_date(date_string):
    from dateutil import parser

    try:
        # Attempt to parse the date string
        parsed_date = parser.parse(date_string)
        return True
    except ValueError:
        # If parsing fails, the date string is not valid
        return False


@pytest.mark.parametrize("input", good_data3)
def test_fetchMessages(input):
    date, time, user, message = _fetchMessages(input)
    assert is_valid_date(date) == True
    assert time is not None
    assert user is not None
    assert len(message) > 0


@pytest.mark.parametrize("path", ["tests/test_data/chat4.txt"])
def test_transformData(path):
    df = _transformData(path)
    assert df.isnull().sum().sum() == 0
    assert df.shape == (40, 15)
