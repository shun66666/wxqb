import re

import scrapy
import os

from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime3, getdate, rename_image_name, repair_content2, \
    delete_script_content, repair_content


class FeedsSpiderSpider(scrapy.Spider):
    name = 'feeds_spider'
    allowed_domains = ['feeds.feedburner.com']
    start_urls = ['http://feeds.feedburner.com/']

    def start_requests(self):
        url = 'https://feeds.feedburner.com/securityweek'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        element = etree.HTML(response_text.encode('utf-8'))
        # print(response_text)
        # title_list = element.xpath('//div[@class="col-lg-9"]/a/div/h2/font/font/text()')
        title_list = element.xpath('//item/title/text()')
        print(title_list)
        url_list = element.xpath('//item/link')
        url_list = [tostring(url, encoding="utf-8").decode().replace("<link>", "").replace("\r\n", "").replace("\n ", "") for url in url_list]
        print(url_list)
        publish_time_list = re.findall("<pubDate>(.*?)</pubDate>", response_text)
        publish_time_list = [publish_time.split(", ")[1].replace(" +0000", "") for publish_time in publish_time_list]
        print(publish_time_list)
        print(len(title_list), len(url_list), len(publish_time_list))
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index]
            items["title"] = title
            # items["author"] = author_list[index]
            items["summary"] = ""
            origin_time = publish_time_list[index]
            time = tranforms_datetime3(origin_time)
            date_yesterday = getdate(1)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：securitylab, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            items["publish_time"] = time
            print(time[:10] + " " + time[11:19])
            items["source_type"] = "feeds"
            yield scrapy.Request(
                target_url,
                dont_filter=True,
                callback=self.parse_detail,
                meta={"items": items},
            )

    def parse_detail(self, response):
        items = response.meta["items"]
        target_url = items["target_url"]
        response_text = response.text
        element2 = etree.HTML(response_text)
        content_list = element2.xpath('//*[@id="center"]/div[3]/div[2]/p')
        content_l = "\n".join(
            [tostring(content, encoding="utf-8").decode().replace("\n", "") for content in content_list])
        print(content_l)
        author = element2.xpath('//*[@id="center"]/div[3]/div[1]/div/div/a/text()')[0]
        print(author)
        items["translate_state"] = 2
        items["content"] = content_l
        items["first_icon"] = ""
        items["author"] = author
    #     img_list = element2.xpath('/html/body/main/div/div[1]/div[1]/figure/img/@src')

    #     if img_list:
    #         for index, img_url in enumerate(img_list):
    #             img_item = ImgproItem()
    #             img_name = img_url.split("/")[-1]
    #             img_item["img_name"] = img_name
    #             if index == 0:
    #                 items["first_icon"] = SRC_REPLACE_PATH + "/" + img_name
    #             img_item["minio_name"] = MINIO_PATH + img_name
    #             img_item["img_src"] = img_url
    #             img_item["bucket"] = MINIO_BUCKET
    #             img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
    #             # print(97, img_item)
    #             yield img_item
        print(items)
        yield items
