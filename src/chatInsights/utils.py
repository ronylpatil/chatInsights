import re
import pandas as pd


def _startsWithDateAndTime(s):
    # pattern = '^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) (AM|PM) -'
    pattern = "^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) (am|pm) - "

    result = re.match(pattern, s)
    if result:
        return result
    return False


def _FindAuthor(s):
    patterns = [
        "([\w]+):",  # First Name
        "([\w]+[\s]+[\w]+):",  # First Name + Last Name
        "([\w]+[\s]+[\w]+[\s]+[\w]+):",  # First Name + Middle Name + Last Name
        "([+]\d{1} [(]\d{3}[)] \d{3}-\d{4}):",  # +1 (205) 962-9343
        "([+]\d{2} \d{5} \d{5}):",  # Mobile Number (India no.)
        "([+]\d{2} \d{3} \d{3} \d{4}):",  # Mobile Number (US no.)
        "([+]\d{2} \d{2} \d{5}-\d{4}):",  # +55 11 99224-4030
        "([+]\d{2} \d{4} \d{3} \d{3}):",  # +91 6370 376 940
        "([+]\d{2} \d{4} \d{4}):",  # +65 8454 7719     +353 83 015 8907
        "([+]\d{2} \d{3} \d{3} \d{3}):",
        "([+]\d{2} \d{4} \d{6}):",
        "([+]\d{3} \d{2} \d{3} \d{4}):",
        "([+]\d{3} \d{3} \d{3} \d{4}):",  # +234 810 631 1539
        "([\w]+)[\u263a-\U0001f999]+:",  # Name and Emoji
    ]
    pattern = "^" + "|".join(patterns)
    result = re.match(pattern, s)
    if result:
        return result
    return False


def _getDataPoint(line):
    splitLine = line.split(" - ")
    dateTime = splitLine[0]
    date, time = dateTime.split(", ")
    message = " ".join(splitLine[1:])
    if _FindAuthor(message):
        splitMessage = message.split(": ")
        author = splitMessage[0]
        message = " ".join(splitMessage[1:])
    else:
        author = None

    return date, time, author, message


def _processing(file_path):
    parsedData = []

    with open(file_path, "r", encoding="utf-8") as fp:
        fp.readline()
        fp.readline()
        messageBuffer = []

        date, time, author = None, None, None
        while True:
            line = fp.readline().replace("\u202f", " ")
            if not line:
                break
            line = line.strip()
            if _startsWithDateAndTime(line):
                if len(messageBuffer) > 0:
                    parsedData.append(
                        [
                            date,
                            time,
                            author,
                            re.sub(r"\s+", " ", " ".join(messageBuffer)),
                        ]
                    )
                messageBuffer.clear()
                date, time, author, message = _getDataPoint(line)
                messageBuffer.append(message)
            else:
                messageBuffer.append(line)

    return pd.DataFrame(parsedData, columns=["date", "time", "user", "message"])
