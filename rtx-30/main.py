from bs4 import BeautifulSoup
import urllib3
import re
import os

# Create credentials.py (git ignored) and specify your phone number, e.g. PHONE_NUMBER = "+4512345678"
from credentials import PHONE_NUMBER


class ScraperReporter(object):
    def __init__(self):
        self.cards = {}
    
    def addScraper(self, card):
        self.cards[card.name] = card

    def notify(self, message, url):
        """Make sure to `brew install terminal-notifier`"""
        t = '-title {!r}'.format('🥳')
        m = '-message {!r}'.format(message)
        l = '-open {!r}'.format(url)
        os.system('terminal-notifier {}'.format(' '.join([t,m,l])))

    def sendiMessage(self, message):
        os.system("osascript sendMessage.scpt "+PHONE_NUMBER+" "+"'"+message+"' ")

    def report(self):
        for name, card in self.cards.items():
            stocklevel = card.getStockLevel()
            card.report()
            if stocklevel > 0:
                message = name+": "+str(stocklevel)+" in stock!"
                self.notify(message, card.url)
                self.sendiMessage(message+" "+card.url)


class Scraper(ScraperReporter):
    def __init__(self, reporter, name=""):
        if name == "":
            self.name = html_class_name
        else:
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
    komplett_rtx3060Ti_gigabyte.setPattern("(\d+) stk. på lager")

    Scraper_Reporter.report()

