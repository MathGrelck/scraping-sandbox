from bs4 import BeautifulSoup
import urllib3
import re
import os
import sys
import json
from json.decoder import JSONDecodeError
import time
import datetime
from threading import Thread

# Create credentials.py (git ignored) and specify your phone number, e.g. PHONE_NUMBER = "+4512345678"
from credentials import PHONE_NUMBER


class ScraperReporter(object):
    def __init__(self):
        self.scraping_status = {'start-time': datetime.datetime.now().isoformat()}
        
        with open('status.json','a+') as f:
            f.seek(0)
            try:
                self.scraping_status = json.load(f)
            except JSONDecodeError:
                # first run, empty status file
                json.dump(self.scraping_status, f, indent=4)

        self.scrapers = {}
    
    def addScraper(self, scraper):
        self.scrapers[scraper.name] = scraper

    def notify(self, message, url):
        """Make sure to `brew install terminal-notifier`"""
        t = '-title {!r}'.format('ALERT')
        m = '-message {!r}'.format(message)
        l = '-open {!r}'.format(url)
        os.system('terminal-notifier {}'.format(' '.join([t,m,l])))

    def sendiMessage(self, message):
        os.system("osascript sendMessage.scpt "+PHONE_NUMBER+" "+"'"+message+"' ")

    def report(self):
        for name, scraper in self.scrapers.items():
            stocklevel = scraper.getStockLevel()
            if stocklevel > 0:
                self.scraping_status[name]['latest-time'] = datetime.datetime.now().isoformat()
                self.scraping_status[name]['stocklevel'] = stocklevel
                if not ('notified-time' in self.scraping_status[name].keys()):
                    self.scraping_status[name]['notified-time'] = datetime.datetime.now().isoformat(),
                    self.scraping_status[name]['url'] = scraper.url
                    message = name+": "+str(stocklevel)+" in stock!"
                    self.notify(message, scraper.url)
                    self.sendiMessage(message+" "+scraper.url)
                with open('status.json','w+') as f:
                    json.dump(self.scraping_status, f, indent=4)


class Scraper(ScraperReporter):
    def __init__(self, reporter, name=""):
        self.name = name
        self.url = None
        self.html_class_name = None
        self.pattern = None
        self.stocklevel = 0
        reporter.addScraper(self)

    def setUrl(self, url):
        self.url = url

    def setHtmlClassName(self, html_class_name):
        self.html_class_name = html_class_name

    def setPattern(self, pattern):
        self.pattern = pattern

    def getStockLevel(self):
        if not self.url:
            print("Please set url using setUrl.")
            return
        if not self.html_class_name:
            print("Please specify html class using setHtmlClassName.")
            return
        if not self.pattern:
            print("Please specify pattern using setPattern.")
            return
        http = urllib3.PoolManager()
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:50.0) Gecko/20100101 Firefox/50.0'}
        response = http.request('GET', self.url, headers=headers)
        soup = BeautifulSoup(response.data.decode('utf-8'),"html.parser")
        elems = soup.find_all(class_=self.html_class_name)
        lvl = 0
        for elem in elems:
            stock_status_string = re.search(self.pattern, str(elem))
            if stock_status_string:
                stock_level = re.search("\d+", str(stock_status_string.group()))
                if stock_level:
                    lvl += int(stock_level.group())
        self.stocklevel = lvl
        return self.stocklevel
    
    def report(self):
        print(self.name + " " + self.url + " " + self.html_class_name)
        print("Stock level: " + str(self.stocklevel))


answer = None
def check():
    global answer
    answer = input("Enter any character to quit, then hit enter: ")


if __name__ == "__main__":
    Scraper_Reporter = ScraperReporter()
    # Test for positive stock
    gt710_msi = Scraper(Scraper_Reporter, name="gt710_msi")
    gt710_msi.setUrl("https://www.proshop.dk/Grafikkort/MSI-GeForce-GT-710-Silent-2GB-GDDR3-RAM-Grafikkort/2532822")
    gt710_msi.setHtmlClassName("site-stock pull-right")
    gt710_msi.setPattern("\d+")

    # Proshop
    proshop_rtx3060Ti_asus = Scraper(Scraper_Reporter, name="Proshop Asus")
    proshop_rtx3060Ti_asus.setUrl("https://www.proshop.dk/Grafikkort/ASUS-GeForce-RTX-3060-Ti-TUF-OC-8GB-GDDR6-RAM-Grafikkort/2886986")
    proshop_rtx3060Ti_asus.setHtmlClassName("site-stock pull-right")
    proshop_rtx3060Ti_asus.setPattern("\d+")
    
    proshop_rtx3060Ti_gigabyte = Scraper(Scraper_Reporter, name="Proshop Gigabyte")
    proshop_rtx3060Ti_gigabyte.setUrl("https://www.proshop.dk/Grafikkort/GIGABYTE-GeForce-RTX-3060-Ti-GAMING-OC-PRO-8GB-GDDR6-RAM-Grafikkort/2887738")
    proshop_rtx3060Ti_gigabyte.setHtmlClassName("site-stock pull-right")
    proshop_rtx3060Ti_gigabyte.setPattern("\d+")

    # Komplett
    komplett_rtx3060Ti_gigabyte = Scraper(Scraper_Reporter, name="Komplett Gigabyte")
    komplett_rtx3060Ti_gigabyte.setUrl("https://www.komplett.dk/product/1174510/hardware/pc-komponenter/grafikkort/gigabyte-geforce-rtx-3060-ti-gaming-oc-pro")
    # komplett_rtx3060Ti_gigabyte.setUrl("https://www.komplett.dk/product/921791/hardware/pc-komponenter/grafikkort/asus-geforce-gt-1030-2gb-silent")
    komplett_rtx3060Ti_gigabyte.setHtmlClassName("stockstatus-stock-details")
    komplett_rtx3060Ti_gigabyte.setPattern("(\d+) stk. p&#xE5; lager")

    Thread(target = check).start()
    while True:
        Scraper_Reporter.report()
        for t in range(30):
            time.sleep(1)
            if answer != None:
                exit()

