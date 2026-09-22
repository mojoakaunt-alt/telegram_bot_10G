
import csv, io, os, requests
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

def normalize_time(x):
    if not x:
        return ""

    x = str(x).strip()

    x = x.replace(".", ":")

    if ":" not in x:
        return ""

    parts = x.split(":")

    if len(parts) != 2:
        return ""

    h = parts[0].zfill(2)
    m = parts[1].zfill(2)

    return f"{h}:{m}"

@lru_cache()
def get_lessons():
    url=os.getenv("SHEET_URL")
    text=requests.get(url).text
    result=[]

    for row in csv.DictReader(io.StringIO(text)):
        if not row.get("Предмет"):
            continue
        row["Початок"]=normalize_time(row.get("Початок",""))
        row["Кінець"]=normalize_time(row.get("Кінець",""))
        result.append(row)

    return result

def clear_cache():
    get_lessons.cache_clear()
