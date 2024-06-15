import re
import pandas as pd
from typing import Union, Match


def _startsWithDateAndTime(s: str) ->  Union[Match[str], bool]:
    pattern = "^([0-9]+)(\/)([0-9]+)(\/)([0-9][0-9]), ([0-9]+):([0-9][0-9]) (am|pm) - "

    result = re.match(pattern, s)
    if result:
        return result
    return False


def _FindAuthor(s: str) -> Union[Match[str], bool]:
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


def _getDataPoint(line: str) -> tuple:
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


def _fetch(file_path: str) -> pd.DataFrame:
    from datetime import datetime

    URLPATTERN = r"(https?://\S+)"
    MEDIAPATTERN = r"<Media omitted>"

    parsedData = []

    with open(file_path, "r", encoding="utf-8") as fp:
        fp.readline()
        fp.readline()
        messageBuffer: list[str] = []

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

    df = pd.DataFrame(parsedData, columns=["date", "time", "user", "message"])

    df = df.dropna()
    df = df.reset_index(drop=True)
    df["words"] = df["message"].apply(
        lambda s: len(s.split(" "))
    )  # Count number of word's in each message
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%y")
    df["media_count"] = (
        df["message"].apply(lambda x: re.findall(MEDIAPATTERN, x)).str.len()
    )
    df["url_count"] = df["message"].apply(lambda x: re.findall(URLPATTERN, x)).str.len()

    weeks = {
        0: "Monday",
        1: "Tuesday",
        2: "Wednesday",
        3: "Thrusday",
        4: "Friday",
        5: "Saturday",
        6: "Sunday",
    }
    df["day"] = df["date"].dt.weekday.map(weeks)

    # Converting 12 hour formate to 24 hour.
    lst = []
    for i in df["time"]:
        out_time = datetime.strftime(datetime.strptime(i, "%I:%M %p"), "%H:%M")
        lst.append(out_time)
    df["24H_time"] = lst

    df["hours"] = df["24H_time"].apply(lambda x: x.split(":")[0])

    df["msg_count"] = df["date"].map(df["date"].value_counts().to_dict())

    df["year"] = df["date"].dt.year

    df["mon"] = df["date"].dt.month
    months = {
        1: "Jan",
        2: "Feb",
        3: "Mar",
        4: "Apr",
        5: "May",
        6: "Jun",
        7: "Jul",
        8: "Aug",
        9: "Sep",
        10: "Oct",
        11: "Nov",
        12: "Dec",
    }
    df["month"] = df["mon"].map(months)
    df.drop("mon", axis=1, inplace=True)
    df["month_year"] = df.apply(lambda x: x["month"] + " " + str(x["year"]), axis=1)
    df["msg_count_monthly"] = df["month_year"].map(
        df["month_year"].value_counts().to_dict()
    )

    return df
