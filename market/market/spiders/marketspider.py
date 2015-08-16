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
    csvHeader = ["Symbol", "Price", "Date", "Volume", "Rating", "RatingVoteCount", "OneYearEstimate"]
    dataList = []
    writtenHeader = False

    def __init__(self, name=None, **kwargs):
        if name is not None:
            self.name = name
        elif not getattr(self, 'name', None):
            raise ValueError("%s must have a name" % type(self).__name__)
        self.__dict__.update(kwargs)
        if not hasattr(self, 'start_urls'):
            self.start_urls = []
        self.getUrls()
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
        rating = hxs.xpath('//*[@id="quotes_content_left_OverallStockRating1_lblPercentage"]/text()').extract()
        ratingVoteCount = hxs.xpath('//*[@id="quotes_content_left_OverallStockRating1_lblTotalRatingsCount"]/text()').extract()
        oneYearEstimate = hxs.xpath('//*[@id="quotes_content_left__1YearTargetEstimate"]/text()').extract()
        writerList = []

        #stock
        writerList.append(self.extractValue(stock, "NULL"))

        #price
        writerList.append(self.extractValue(price, "NULL"))

        #date
        millis = int(round(time.time() * 1000))
        writerList.append(millis)

        #volume
        writerList.append(self.extractValue(volume, 0))

        #rating
        writerList.append(self.extractValue(rating, "NULL"))

        #ratingVoteCount
        writerList.append(self.extractValue(ratingVoteCount, "NULL"))

        #oneYearEstimate
        writerList.append(self.extractValue(oneYearEstimate, "NULL"))

        self.appendCSV(writerList)
        #spider stuff
        item = MarketSpider()
        yield item

    def start_requests(self):
        utc = datetime.utcnow()
        beforeMarketCloses = utc.hour <= 21 and utc.minute <= 20
        afterMarketOpens = utc.hour >= 14 and utc.minute >= 10
        isMarketDay = utc.weekday() < 6 #0 is Monday, 6 is Sunday
        #if(True):
        if(isMarketDay and beforeMarketCloses and afterMarketOpens):
            for url in self.start_urls:
                yield self.make_requests_from_url(url)

    def getUrls(self):
        with open(self.data_folder + 'companylist.csv', 'rb') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                if row[0] != "Symbol":
                    self.concatUrls(row[0].replace(" ",""))

    def concatUrls(self, symbol):
        self.start_urls.append("http://www.nasdaq.com/symbol/" + symbol + "/real-time")


    def appendCSV(self, writeList):
        with open (self.data_folder + self.data_file, "a") as csvfile:
            stockwriter = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            if(not self.writtenHeader):
                stockwriter.writerow(self.csvHeader)
                self.writtenHeader = True
            stockwriter.writerow(writeList)

    def extractValue(self, value, default):
        if(len(value) > 0):
            value = value[0].encode('ascii', 'ignore')
        else:
            value = default
        return value
