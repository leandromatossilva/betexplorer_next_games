import requests
import utils
import datetime
import os.path
import scraps


from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.common.by import By


from constants import BASE_URL, HOME_URL, BOOKMAKERS_SCRAP, LEAGUES_SCRAP


# Get Current Date
date_scraping = datetime.date.today()



options = Options()
# options.binary_location = "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
driver = webdriver.Chrome(options=options, executable_path="C:\\Users\\leandro.silva\\Documents\\chromedriver.exe")
cookies = {
    "my_timezone": "-4"
}

for SET in LEAGUES_SCRAP:
    for league in SET['leagues']:
        URL = BASE_URL + SET['country'] + '/' + league

        event = {'league': league, 'country': SET['country'], 'fin': False}

        page = requests.get(
            URL,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                              '(KHTML, like Gecko) Chrome/103.0.5060.53 Safari/537.36'
            },
            cookies=cookies
        )

        bsoup = BeautifulSoup(page.text, 'html.parser')

        table = bsoup.find('table', attrs={'class': 'table-main'})
        trs = table.find_all('tr')

        event['season'] = bsoup.find('h1', attrs={'class': 'wrap-section__header__title'})\
            .find('span', attrs={'class': 'tablet-desktop-only'}).text.split(' ')[-1]

        for tr in trs:
            links = tr.find_all('a')
            if not links:
                continue
            else:
                event['path'] = (links[0]['href']).split('/')[-2]
                event['link'] = URL_1X2 = HOME_URL + links[0]['href']
                tds = tr.find_all('td')
                if tds:
                    event['home_team'] = tds[1].text.split(' - ')[0]
                    event['away_team'] = tds[1].text.split(' - ')[1]
                    print(tds[1].text)

                    URL_DOUBLE_CHANCE = event['link'] + "#dc"
                    URL_BOTH_TEAMS_SCORE = event['link'] + "#bts"
                    URL_OVER_UNDER = event['link'] + "#ou"
                    URL_ASIAN_HAND = event['link'] + "#ah"

                print("1X2")
                r = scraps.scrap_odds(event, '1X2', driver, date_scraping, URL_1X2)
                while r is False:
                    print('r is false')
                    r = scraps.scrap_odds(event, '1X2', driver, date_scraping, URL_1X2)

                print("DOUBLE_CHANCE")
                r = scraps.scrap_odds(event, '1X2', driver, date_scraping, URL_DOUBLE_CHANCE)
                while r is False:
                    print('r is false')
                    r = scraps.scrap_odds(event, '1X2', driver, date_scraping, URL_DOUBLE_CHANCE)


