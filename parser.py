import logging
import time
import articleZen
import os
import sys
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('Parser')


class YandexZenParser:

    def __init__(self):
        self.parsedUrl = []
        self.rootURL = "https://zen.yandex.ru"
        self.channels = '/media/zen/channels'
        self.outputPath = 'output/'
        self.parsedFileName = 'parsed.txt'
        self.articleCounter = 0
        self.channelCounter = 0
        self.driver = self.initDriver()
        self.loadEnv()

    def loadEnv(self):
        if os.path.isdir(self.outputPath):
            if os.path.isfile(self.outputPath + self.parsedFileName):
                with open(self.outputPath + self.parsedFileName, 'r') as file:
                    for line in file:
                        self.parsedUrl.append(line[:-1])
        else:
            os.mkdir(self.outputPath)

    def appendParsed(self, url):
        self.parsedUrl.append(url)

        with open(self.outputPath + self.parsedFileName, 'a') as file:
            file.write(url + '\n')

    def initDriver(self):
        chrome_options = Options()
        chrome_options.add_argument("--window-size=1920x1080")
        driver = webdriver.Chrome(options=chrome_options)
        return driver

    def printStats(self):
        logger.info("All sessions parsed %d URLs." % len(self.parsedUrl))
        logger.info("In this session parsed %d articles." % self.articleCounter)
        logger.info("In this session parsed %d channels." % self.channelCounter)

    def close(self):
        self.driver.close()

    def tryParseArticle(self, url):
        try:
            url = url[:url.find('?')]
            logger.info("Try parse article " + url)
            if not url.startswith(self.rootURL):
                logger.info("This URL must have domain zen.yandex.ru!")
                return

            if url in self.parsedUrl:
                logger.info("This URL has been parsed yet! ")
                return


            self.driver.get(url)
            time.sleep(1)
            data = self.driver.page_source
            article = articleZen.Article(data)
            outputFilePath = self.outputPath + url[url.rfind('/') + 1:] + ".xml"
            article.save(outputFilePath, url)
            logger.info("Article has been parsed succesfully!")
            self.appendParsed(url)
            self.articleCounter += 1
        except Exception as e:
            logger.error(e)
            logger.error("tryParseArticle has been crashed.")
            return []

    def tryParseChannel(self, url):
        try:
            logger.info("Try parse Channel " + url)
            if url in self.parsedUrl:
                logger.info("This URL has been parsed yet! ")
                return
            self.driver.get(self.rootURL + url)

            i = 0
            lastHeight = 0
            limit = 100
            while True:
                self.driver.execute_script("window.scrollTo(0, %d);" % (lastHeight + 1000))
                time.sleep(1)
                i += 1
                newHeight = self.driver.execute_script("return document.body.scrollHeight")
                if i > limit or lastHeight == newHeight:
                    break
                lastHeight = newHeight

            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            for link in soup.find_all("a", {"class": "card-image-view__clickable"}):
                self.tryParseArticle(link['href'])

            logger.info("Channel has been parsed succesfully!")
            self.appendParsed(url)
            self.channelCounter += 1
        except:
            logger.error("tryParseChannel has been crashed.")
            return []

    def getChannelsStack(self, index):
        try:
            logger.info("Getting %d stack of channels." % index)
            self.driver.get(self.rootURL + self.channels + "?page=%d" % index)
            soup = BeautifulSoup(self.driver.page_source, 'lxml')
            return list(map(lambda tag: tag["href"], soup.find_all("a", {"class" : "channel-item__link"})))
        except:
            logger.error("getChannelsStack has been crashed.")
            return []

    def run(self, start=1, end=1000000):
        logger.info("Start parsing of Yandex Zen.")
        for i in range(start, end):
            for channelURL in self.getChannelsStack(i):
                self.tryParseChannel(channelURL)


if __name__ == '__main__':
    parser = YandexZenParser()
    print(sys.argv)
    if len(sys.argv) == 1:
        parser.run()
    elif len(sys.argv) == 3:
        start = int(sys.argv[1])
        end = int(sys.argv[2])
        if 0 < start < end:
            parser.run(start, end)
        else:
            print("Must be 0 < start < end!")
    else:
        print("parser.py <startIndex> <endIndex>")

    parser.printStats()
    parser.close()

