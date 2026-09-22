
import csv, io, os, requests
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

def normalize_time(x):
    x=str(x).replace(".",":").strip()
    if len(x)==4:
        x="0"+x
    return x

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
