# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PttimagecrawlItem(scrapy.Item):
    title = scrapy.Field()         # 文章名稱，用於形成個別資料夾名稱
    image_urls = scrapy.Field()    # 每張圖片URL的位址
    images = scrapy.Field()        # 不可更改，pippelines會用到
    image_paths = scrapy.Field()   # 不可更改，pippelines會用到
