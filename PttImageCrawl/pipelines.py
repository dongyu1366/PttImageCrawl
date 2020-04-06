# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import scrapy
import os
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
from scrapy.utils.project import get_project_settings
from scrapy.utils.misc import md5sum


class PttimagecrawlPipeline(ImagesPipeline):
    def get_media_requests(self, item, info):
        request_objs = super(PttimagecrawlPipeline, self).get_media_requests(item, info)

        # 為每個request_obj物件新增item屬性
        for request_obj in request_objs:
            request_obj.item = item
        return request_objs # 父類中必須返回這個列表，給其他函式使用

    def file_path(self, request, response=None, info=None):
        # path獲取父類中file_path方法返回的值‘full/hash.jpg'，hash是圖片的雜湊值
        path = super(PttimagecrawlPipeline, self).file_path(request, response, info)
        category = request.item.get('title')                 #request即前一個函式返回的列表中的每一項，所以有item屬性
        category_path = os.path.join(category)               # 建立每個種類的路徑
        image_name = path.replace('full/', '')               # 去掉原本的'full/'，只留下hash值作為檔名
        image_path = f'{category_path}/{image_name}'         # 圖片完整的路徑和檔名
        return image_path

    # 更改圖片儲存方式，使其能正確下載gif
    def check_gif(self, image):
        if image.format is None:
            return True

    def persist_gif(self, key, data, info):
        absolute_path = self.store._get_filesystem_path(key)
        self.store._mkdir(os.path.dirname(absolute_path), info)
        f = open(absolute_path, 'wb')  # use 'b' to write binary data.
        f.write(data)

    def image_downloaded(self, response, request, info):
        checksum = None
        for path, image, buf in self.get_images(response, request, info):
            if checksum is None:
                buf.seek(0)
                checksum = md5sum(buf)
                width, height = image.size
            if self.check_gif(image):
                self.persist_gif(path, response.body, info)
            else:
                self.store.persist_file(
            path, buf, info,
            meta={'width': width, 'height': height},
            headers={'Content-Type': 'image/jpeg'})
        return checksum



# 刪除沒有圖片的項目
class DropItemPipeline(object):
    def process_item(self, item, spider):
        if item['image_urls']:
            return item
        else:
            raise DropItem(f'<<<{item["title"]}>>>無圖片')
