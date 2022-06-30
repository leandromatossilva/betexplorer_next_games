import time
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from constants import BOOKMAKERS_SCRAP, ARCHIVE_ODDS_URL
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By


def scrap_odds(event_link, market_name, driver, event_path, date_scraping):
    driver.get(event_link)
    driver.refresh()
    time.sleep(2)
    soup = None

    try:
        WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located(('id', 'sortable-1')))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        r = True
    except TimeoutException:
        try:
            WebDriverWait(driver, timeout=10).until(EC.presence_of_element_located(('id', 'no-odds-info')))
            r = True
        except TimeoutException:
            r = False

    if soup:
        table = soup.find('table', attrs={'id': 'sortable-1'})
        if table is not None:
            trs = table.find('tbody').find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                bookmaker = tds[0].text
                if bookmaker in BOOKMAKERS_SCRAP:
                    odds = tr.find_all(attrs={'class': 'table-main__detail-odds'})

                    odd_home = odds[0]
                    last_odd_home = odd_home['data-odd']
                    date_last_odd_home = odd_home['data-created']

                    odd_draw = odds[1]
                    last_odd_draw = odd_draw['data-odd']
                    date_last_odd_draw = odd_draw['data-created']

                    odd_away = odds[2]
                    last_odd_away = odd_away['data-odd']
                    date_last_odd_away = odd_away['data-created']

                    try:
                        data_bid_home = odd_home['data-bid']
                        data_oid_home = odd_home['data-oid']
                    except KeyError:
                        data_oid_home = data_bid_home = ''
                        
                    try:
                        data_bid_draw = odd_draw['data-bid']
                        data_oid_draw = odd_draw['data-oid']
                    except KeyError:
                        data_oid_draw = data_bid_draw = ''
                        
                    try:
                        data_bid_away = odd_away['data-bid']
                        data_oid_away = odd_away['data-oid']
                    except KeyError:
                        data_oid_away = data_bid_away = ''
                        
                    if (data_bid_home and data_oid_home) != '':
                        archive_odds_home_url = ARCHIVE_ODDS_URL + data_oid_home + '/' + data_bid_home
                        archive_odds = get_archive_odds(event_link, archive_odds_home_url)
                        print('BOOKMAKER | ODD DATE | ODD | VARIACAO | EVENT')
                        for odds in archive_odds:
                            print(f"{bookmaker} | {odds['date']} | {odds['odd']} | {odds['change']} | {event_path}")

                    if (data_bid_draw and data_oid_draw) != '':
                        archive_odds_draw_url = ARCHIVE_ODDS_URL + data_oid_draw + '/' + data_bid_draw
                        archive_odds = get_archive_odds(event_link, archive_odds_draw_url)
                        print('BOOKMAKER | ODD DATE | ODD | VARIACAO | EVENT')
                        for odds in archive_odds:
                            print(f"{bookmaker} | {odds['date']} | {odds['odd']} | {odds['change']} | {event_path}")

                    if (data_bid_away and data_oid_away) != '':
                        archive_odds_away_url = ARCHIVE_ODDS_URL + data_oid_away + '/' + data_bid_away
                        archive_odds = get_archive_odds(event_link, archive_odds_away_url)
                        print('BOOKMAKER | ODD DATE | ODD | VARIACAO | EVENT')
                        for odds in archive_odds:
                            print(f"{bookmaker} | {odds['date']} | {odds['odd']} | {odds['change']} | {event_path}")

    return r


def get_archive_odds(event_link, archive_odds_url):
    URL_API = archive_odds_url
    archive_odds = requests.get(URL_API,
                                headers={
                                    'referer': event_link,
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                  '(KHTML, like Gecko) Chrome/99.0.4844.51 Safari/537.36'
                                }).json()

    return archive_odds
