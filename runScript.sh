#!/bin/bash

pathToScraper=/home/morgan/code/WebScraper/market
pathToLogFile=/home/morgan/code/WebScraper/data/logfile.log

echo "startingRunning ##################################" >> $pathToLogFile
cd $pathToScraper
echo $pathToLogFile
PATH=$PATH:/usr/local/bin
export PATH
scrapy crawl MarketSpider &>> $pathToLogFile
echo "stoppedRunning ###################################" >> $pathToLogFile
