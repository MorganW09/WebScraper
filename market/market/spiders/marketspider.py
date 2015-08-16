from scrapy.spider     import Spider
from scrapy.selector     import HtmlXPathSelector
from market.items    import MarketItem
from scrapy.http    import Request
from scrapy import Selector
import unicodedata
import csv
import time
from datetime import datetime
from os.path import expanduser


class MarketSpider(Spider):
    name = "MarketSpider"
    allowed_domains = ["http://www.nasdaq.com/"]
    data_folder = str(expanduser("~")) + "/code/WebScraper/data/"
    data_file = "stockprices.csv"

    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        if not hasattr(self, 'start_urls'):
            self.start_urls = []
        self.getUrls()
        #today = datetime.date.today()
        utc = str(datetime.utcnow())
        utc = utc.split(".")[0].replace("-", ".").replace(" ", ".").replace(":",".")
        self.data_file = utc + self.data_file

    def parse(self, response):
        hxs = Selector(response)
        #hxs = HtmlXPathSelector(response)
        #titles = hxs.select('//h1[@class="post_title"]/a/text()').extract()
        price = hxs.xpath('//*[@id="qwidget_lastsale"]/text()').extract()
        stock = hxs.xpath('//*[@id="left-quotes-content"]/div[1]/span/a[3]/text()').extract()
        volume = hxs.xpath('//*[@id="quotes_content_left__Volume"]/text()').extract()
        #stock
        stock = stock[0].encode('ascii','ignore')
        #price
        if(len(price) > 0):
            price = price[0].encode('ascii','ignore')
        else:
            price = "NULL"
        #volume
        if(len(volume) > 0):
            volume = volume[0].encode('ascii','ignore').replace(",","")
        else:
            volume = 0
        self.appendStock(stock, price, volume)
        #spider stuff
        item = MarketSpider()
        yield item

    def start_requests(self):
        utc = datetime.utcnow()
        beforeMarket = utc.hour <= 21 and utc.minute <= 20
        afterMarket = utc.hour >= 14 and utc.minute >= 10
        marketDay = utc.weekday() < 6 #0 is Monday, 6 is Sunday
        if(True):
        #if(marketDay and beforeMarket and afterMarket):
            for url in self.start_urls:
                yield self.make_requests_from_url(url)

    def getUrls(self):
        print ("from getUrls()")
        #self.start_urls = ["http://www.nasdaq.com/symbol/aapl/real-time"]
        with open(self.data_folder + 'companylist.csv', 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                self.concatUrls(row[0])

    def concatUrls(self, symbol):
        self.start_urls.append("http://www.nasdaq.com/symbol/" + symbol + "/real-time")

    def appendStock(self, stock, price, volume):
        millis = int(round(time.time() * 1000))
        with open(self.data_folder + self.data_file, "a") as myfile:
            myfile.write(stock + "," + price + "," + str(millis) + "," + str(volume) + "\n")
