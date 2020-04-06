# -*- coding: utf-8 -*-
import scrapy
from ..items import PttimagecrawlItem


# 篩選符合圖片格式的URL
def isImageFormat(link):
    if(link.find('.jpg') > -1 or link.find('.png') > -1 or link.find('.gif') > -1 or link.find('.jpeg') > -1):
       return True
    return False

# 移除特殊字元(移除無法作為資料夾的字元)
def remove(char, deletechars):
    for c in deletechars:
        char = char.replace(c,'')
    return char.strip()

class ImageSpider(scrapy.Spider):
    name = 'image'
    allowed_domains = ['ptt.cc']
    start_urls = ['https://www.ptt.cc/bbs/Beauty/index.html']

    # 計數器，用來限制總共要抓幾頁的資料
    count = 0
    count_max = 2

    # 因表特板有年齡限制，需先通過年齡驗證，才能取得頁面
    def parse(self, response):
        url = 'https://www.ptt.cc/bbs/Beauty/index.html'
        yield scrapy.Request(url=url, cookies={'over18': '1'}, callback=self.parse_list)

    # 文章列表的頁面
    def parse_list(self, response):
        # 取得本頁面每篇文章的title, URL
        for quote in response.css('div.r-ent'):
            quote_title = quote.css('div.title a::text').get()
            quote_href = 'https://www.ptt.cc' + str(quote.css('div.title a::attr(href)').get())

            item = PttimagecrawlItem()
            if quote_title:
                item['title'] = remove(quote_title, "?:\*/'<>.;&!|`{}")     # 儲存文章名稱，之後用於資料夾命名

                yield scrapy.Request(quote_href, callback=self.parse_content, meta={'item': item})

        # 獲取下一頁的URL(其實是翻上頁)，這裡用xpath路徑，因為css路徑太長了
        previous_page = response.xpath('//*[@id="action-bar-container"]/div/div[2]/a[2]/@href').get()

        # 判斷是否要爬下一頁
        self.count += 1
        if self.count < self.count_max:
            if previous_page is not None:
                previous_page = response.urljoin(previous_page)
                yield scrapy.Request(previous_page, callback=self.parse_list)

    # 文章內容頁面
    def parse_content(self, response):
        item = response.meta['item']

        #取得每篇文章內的圖片URL
        img_urls = []
        for img in response.xpath('//*[@id="main-content"]/a/@href').getall():
            # 判斷此URL到底是不是img_url
            if(isImageFormat(img)):
               img_urls.append(img)

        item['image_urls'] = img_urls

        return  item
