import time
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from constants import BOOKMAKERS_SCRAP, ARCHIVE_ODDS_URL
from bs4 import BeautifulSoup
from datetime import datetime, timedelta


def scrap_odds(event, market_name, driver, date_scraping, url):
    driver.get(url)
    driver.refresh()
    time.sleep(3)
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
        # event['match_date_time'] = (datetime.strptime(get_match_date(soup), '%d.%m.%Y - %H:%M') - timedelta(hours=5))
        # print(f"{event['path']} | {event['home_team']} | {event['away_team']} | {event['match_date_time']} | {event['season']} | {event['league']} | {event['country']} | {date_scraping}")
        table = soup.find('table', attrs={'id': 'sortable-1'})
        if table is not None:
            trs = table.find('tbody').find_all('tr')
            for tr in trs:
                tds = tr.find_all('td')
                bookmaker = tds[0].text
                if bookmaker in BOOKMAKERS_SCRAP:
                    odds = tr.find_all(attrs={'class': 'table-main__detail-odds'})

                    try:    
                        odd_home = odds[0]
                        last_odd_home = odd_home['data-odd']
                        date_last_odd_home = odd_home['data-created']
                    except:
                        odd_home = {}
                        
                    try:    
                        odd_draw = odds[1]
                        last_odd_draw = odd_draw['data-odd']
                        date_last_odd_draw = odd_draw['data-created']
                    except:
                        odd_draw = {}
                        
                    try:    
                        odd_away = odds[2]
                        last_odd_away = odd_away['data-odd']
                        date_last_odd_away = odd_away['data-created']
                    except:
                        odd_away = {}

                    try:
                        # hasattr(odd_home, 'data-bid')
                        # hasattr(odd_home, 'data-oid')
                        data_oid_home = odd_home['data-oid']
                        data_bid_home = odd_home['data-bid']
                    except KeyError:
                        print('Except')
                        data_oid_home = data_bid_home = ''
                        # odd_home['data-oid'] = odd_home['data-bid'] = None

                    try:
                        # hasattr(odd_draw, 'data-bid')
                        # hasattr(odd_draw, 'data-oid')
                        data_oid_draw = odd_draw['data-oid']
                        data_bid_draw = odd_draw['data-bid']
                    except KeyError:
                        print('Except')
                        data_oid_draw = data_bid_draw = ''
                        # odd_draw['data-oid'] = odd_draw['data-bid'] = None

                    try:
                        # hasattr(odd_away, 'data-bid')
                        # hasattr(odd_away, 'data-oid')
                        data_oid_away = odd_away['data-oid']
                        data_bid_away = odd_away['data-bid']
                    except KeyError:
                        print('Except')
                        data_oid_away = data_bid_away = ''
                        # odd_away['data-oid'] = odd_away['data-bid'] = None

                    if (data_oid_home and data_bid_home) != '':
                        archive_odds_home_url = ARCHIVE_ODDS_URL + data_oid_home + '/' + data_bid_home
                        archive_odds = get_archive_odds(event['link'], archive_odds_home_url)
                        # print('BOOKMAKER | ODD DATE | ODD | VARIACAO | EVENT')
                        for idx, odds in enumerate(archive_odds):
                            if idx == 0:
                                last_odd_home_change = round(float(last_odd_home) - float(odds['odd']), 2)
                            print(f"{bookmaker} | {odds['date']} | {odds['odd']} | {odds['change']} | {event['path']}")

                    if (data_oid_draw and data_bid_draw) != '':
                        archive_odds_draw_url = ARCHIVE_ODDS_URL + data_oid_draw + '/' + data_bid_draw
                        archive_odds = get_archive_odds(event['link'], archive_odds_draw_url)
                        # print('BOOKMAKER | ODD DATE | ODD | VARIACAO | EVENT')
                        for idx, odds in enumerate(archive_odds):
                            if idx == 0:
                                last_odd_draw_change = round(float(last_odd_draw) - float(odds['odd']), 2)
                            print(f"{bookmaker} | {odds['date']} | {odds['odd']} | {odds['change']} | {event['path']}")

                    if (data_oid_away and data_bid_away) != '':
                        archive_odds_away_url = ARCHIVE_ODDS_URL + data_oid_away + '/' + data_bid_away
                        archive_odds = get_archive_odds(event['link'], archive_odds_away_url)
                        # print('BOOKMAKER | ODD DATE | ODD | VARIACAO | EVENT')
                        for idx, odds in enumerate(archive_odds):
                            if idx == 0:
                                last_odd_away_change = round(float(last_odd_away) - float(odds['odd']), 2)
                            print(f"{bookmaker} | {odds['date']} | {odds['odd']} | {odds['change']} | {event['path']}")

    return r


def get_archive_odds(event_link, archive_odds_url):
    URL_API = archive_odds_url
    archive_odds = requests.get(URL_API,
                                headers={
                                    'referer': event_link,
                                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                                                  '(KHTML, like Gecko) Chrome/103.0.5060.66 Safari/537.36'
                                }).json()
    time.sleep(5)
    return archive_odds


def get_match_date(soup):
    match_date = soup.find('div', attrs={'class': 'wrap-page__in'}).find('p', attrs={'id': 'match-date'}).text

    return match_date


def format_to_date(date_betexplorer, timezone):
    try:
        datetime_obj = datetime.strptime(date_betexplorer, '%d,%m,%Y,%H,%M')
        data_hora_brasil = datetime_obj - timedelta(hours=timezone)

        return data_hora_brasil

    except TypeError as error:
        print("Error: ", error)

