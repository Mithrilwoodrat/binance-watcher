import ast
import os.path
import os
import random
import re
import string
import time
import re
import json
from typing import Dict, List, Optional

import requests
import logging

from db_util import Announcement

previously_found_coins = set()
latest_listing=''


def get_announcements() -> List[Dict]:
    """
    Retrieves new coin listing announcements
    """
    logging.debug("Pulling announcement page")
    # Generate random query/params to help prevent caching
    rand_page_size = random.randint(1, 200)
    letters = string.ascii_letters
    random_string = ''.join(random.choice(letters) for i in range(random.randint(10, 20)))
    random_number = random.randint(1, 99999999999999999999)
    queries = ["type=1", "catalogId=48", "pageNo=1", f"pageSize={str(rand_page_size)}", f"rnd={str(time.time())}",
               f"{random_string}={str(random_number)}"]
    random.shuffle(queries)
    logging.debug(f"Queries: {queries}")
    request_url = f"https://www.binancezh.com/gateway-api/v1/public/cms/article/list/query" \
                  f"?{queries[0]}&{queries[1]}&{queries[2]}&{queries[3]}&{queries[4]}&{queries[5]}"
    resp = requests.get(request_url, verify=False, timeout=10)
    try:
        logging.debug(f'X-Cache: {resp.headers["X-Cache"]}')
    except KeyError:
        # No X-Cache header was found - great news, we're hitting the source.
        pass

    announcements = []
    if resp.status_code != 200:
        logging.error("request error")
        return announcements

    latest_announcement = resp.json()
    logging.debug("Finished pulling announcement page")
    logging.debug(latest_announcement)
    data = latest_announcement.get('data')
    if not data :
        logging.error("get data error")
        return announcements
    catalogs = data.get('catalogs')
    if not catalogs or len(catalogs) == 0:
        logging.error("get catalogs error")
        return announcements
    announcements = catalogs[0].get('articles')
    return announcements

def insert_announcements():
    announcements = get_announcements()
    for announcement in announcements:
        title = announcement['title']
        found_coin = 0
        coin_name = ''
        results = re.findall('\(([^)]+)', title)
        if len(results) == 1:
            coin_name = results[0]
        if 'Will List' in title:
            found_coin=1
        announcement_time = announcement['releaseDate']
        print(title)
        exist = Announcement.select().where((Announcement.title == title) & (Announcement.coin_name == coin_name))
        print(len(exist))
        if len(exist) == 0 :
            print("insert")
            record = Announcement.create(title=title, coin_name=coin_name, found_coin=found_coin, announcement_time=announcement_time)
            record.save()


def get_last_coin():
    """
     Returns new Symbol when appropriate
    """
    announcements = get_announcements()
    latest_announcement = announcements[0]['title']
    logging.info("latest_announcement :" + latest_announcement)

    found_coin = re.findall('\(([^)]+)', latest_announcement)
    logging.info
    uppers = None

    if 'Will List' not in latest_announcement or found_coin[0] == latest_listing or \
            found_coin[0] in previously_found_coins:
        return None
    else:
        if len(found_coin) == 1:
            uppers = found_coin[0]
            previously_found_coins.add(uppers)
            logging.info('New coin detected: ' + uppers)
        if len(found_coin) != 1:
            uppers = None
    print('uppers='+uppers)
    return uppers


if __name__ == "__main__":
    logging.getLogger().setLevel(logging.NOTSET)
    logging.basicConfig(format='%(asctime)s %(funcName)s %(lineno)s %(filename)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p', level=logging.INFO)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.WARNING)
    logging.getLogger('web3.providers.HTTPProvider').setLevel(logging.WARNING)
    logging.getLogger('web3.RequestManager').setLevel(logging.WARNING)
    insert_announcements()
    # print(get_announcements())