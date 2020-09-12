import urllib3
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

def cdataPack(text):
    return "\n<![CDATA[%s]]>\n" % text

class Article:
    def __init__(self, doc):
        soup = BeautifulSoup(doc, 'lxml')
        self.title = soup.find("h1", {"class": "article__title"}).text
        strLikesCount = soup.find("span", {"class": "likes-count-minimal__count"}).text
        if strLikesCount.endswith(" тыс."):
            strLikesCount = strLikesCount[:strLikesCount.find(" тыс.") - 1].replace(',', '.')
            self.likeCount = int(float(strLikesCount) * 1000)
        else:
            self.likeCount = int(strLikesCount)
        self.date = soup.find("span", {"class": "article-stat__date"}).text
        self.middleReadingTime = soup.find_all("span", {"class": "article-stat__count"})[1].text
        self.author = soup.find("a", {"class": "publisher-controls__channel-name"}).text
        self.keywords = list((map(lambda tag: tag.text, soup.find_all("span", {"class": "zen-tag-publishers__title"}))))
        self.text = '\n'.join((map(lambda tag: tag.text, soup.find_all("p", {"class": "article-render__block"}))))

    def __str__(self):
        return "Title: {}\nAuthor: {}\nLikeCount: {}\nDate: {}\nMiddleReadingTime: {}\nKeywords: {}\nText: {}\n".\
            format(self.title, self.author, self.likeCount, self.date, self.middleReadingTime, self.keywords, self.text)

    def save(self, filePath, url):
        soup = BeautifulSoup(features='lxml')

        doc = soup.new_tag("doc")
        doc['href'] = url

        tag = soup.new_tag("title")
        tag['auto'] = "true"
        tag['type'] = "str"
        tag['verify'] = "true"
        tag.insert(0, cdataPack(self.title))
        doc.append(tag)

        tag = soup.new_tag("author")
        tag['auto'] = "true"
        tag['type'] = "str"
        tag['verify'] = "true"
        tag.insert(0, cdataPack(self.author))
        doc.append(tag)

        tag = soup.new_tag("likeCount")
        tag['auto'] = "true"
        tag['type'] = "int"
        tag['verify'] = "true"
        tag.insert(0, str(self.likeCount))
        doc.append(tag)

        tag = soup.new_tag("middleReadingTime")
        tag['auto'] = "true"
        tag['type'] = "str"
        tag['verify'] = "true"
        tag.insert(0, cdataPack(self.middleReadingTime))
        doc.append(tag)

        list = soup.new_tag("keywords")
        list['auto'] = "true"
        list['type'] = "list"
        list['verify'] = "true"

        for keyword in self.keywords:
            tag = soup.new_tag("keyword")
            tag['auto'] = "true"
            tag['type'] = "str"
            tag['verify'] = "true"
            tag.string = cdataPack(keyword)
            list.append(tag)

        doc.append(list)

        tag = soup.new_tag("text")
        tag['auto'] = "true"
        tag['type'] = "str"
        tag['verify'] = "true"
        tag.insert(0, cdataPack(self.text))
        doc.append(tag)

        soup.append(doc)
        with open(filePath, 'wb') as file:
            file.write(soup.prettify().encode('UTF-8'))

# for testing
if __name__ == '__main__':
    url = 'https://zen.yandex.ru/media/shebbi_shik/moia-obuv-bolshe-ne-valiaetsia-nasypiu-v-shkafu-pokazyvaiu-kakuiu-prisposobu-dlia-ee-hraneniia-ia-smasterila-5e8af5775698984116bc90e0'
    chrome_options = Options()
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    time.sleep(1)
    data = driver.page_source
    article = Article(data)
    print(article)
    article.save("test.xml", url)
    driver.close()
