import datetime

import scrapy
import os

from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime, getdate, rename_image_name, repair_content2, \
    delete_script_content, repair_content


class CyberscoopSpiderSpider(scrapy.Spider):
    name = 'cyberscoop_spider'
    allowed_domains = ['www.cyberscoop.com']
    start_urls = ['http://www.cyberscoop.com/']

    def start_requests(self):
        url = 'http://www.cyberscoop.com/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        element = etree.HTML(response_text)
        url_list = element.xpath('/html/body/div[2]/section[1]/div[2]/div/a/@href')
        url1_list = element.xpath('/html/body/div[2]/section[2]/div/div/div[2]/div[1]/div/article/div[2]/a/@href')
        url_list.extend(url1_list)
        # print(url_list)
        title_list = element.xpath('/html/body/div[2]/section[1]/div[2]/div/div/h1/text()')
        title1_list = element.xpath('/html/body/div[2]/section[2]/div/div/div[2]/div[1]/div/article/div[2]/a/h3/text()')
        title_list.extend(title1_list)
        # print(title_list)
        author_list = element.xpath("/html/body/div[2]/section[2]/div/div/div[2]/div[1]/div/article/div[2]/div[2]/span/strong/a/text()")
        # print(author_list)
        publish_time_list = element.xpath('/html/body/div[2]/section[2]/div/div/div[2]/div[1]/div/article/div[2]/div[2]/span/strong/text()')
        publish_time_list = [publish_time for publish_time in publish_time_list if publish_time != " "]
        publish_time_list = [publish_time.replace(" | ", "") for publish_time in publish_time_list]
        publish_time_list = [tranforms_datetime(publish_time) for publish_time in publish_time_list]
        # print(publish_time_list)
        summary_list = [""]
        summary1_list = element.xpath('/html/body/div[2]/section[2]/div/div/div[2]/div[1]/div/article/div[2]/div[3]/p/text()')
        summary_list.extend(summary1_list)
        # print(summary_list)
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index]
            items["title"] = title
            if index == 0:
                pass
                items["summary"] = ""
                items["source_type"] = "cyberscoop"
                items["publish_time"] = datetime.datetime.now()
                print(f"报告来源：cyberscoop, 报告时间：{datetime.datetime.now()}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            else:
                items["author"] = author_list[index]
                items["summary"] = summary_list[index]
                items["source_type"] = "cyberscoop"
                origin_time = publish_time_list[index]
                time = origin_time
                date_yesterday = getdate(1)
                date_yesterday = getdate(5)
                if date_yesterday > time[:10]:
                    break
                print(f"报告来源：cyberscoop, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
                items["publish_time"] = time

            yield scrapy.Request(
                target_url,
                dont_filter=True,
                callback=self.parse_detail,
                meta={"items": items},
            )

    def parse_detail(self, response):
        items = response.meta["items"]
        # target_url = items["target_url"]
        # id = target_url.split("/")[-1].split(".")[0]
        response_text = response.text
        element2 = etree.HTML(response_text)
        # 作者,时间
        author_list = element2.xpath('/html/body/div[2]/div/article/div[2]/div[2]/div[2]/a/text()')
        publish_time_list = element2.xpath('/html/body/div[2]/div/article/div[2]/div[2]/div[2]/span/text()')
        items["author"] = author_list[0]
        print(888888888888, tranforms_datetime(publish_time_list[0].split(" | ")[0]))
        items["publish_time"] = tranforms_datetime(publish_time_list[0].split(" | ")[0])
        content_list = element2.xpath(f'/html/body/div[2]/div/article/div[2]/div[2]/div[2]/p')
        content_l = "\n".join([tostring(content, encoding="utf-8").decode().replace("\n", "") for content in content_list])
        # print(content_l)
        img_list = element2.xpath(f'/html/body/div[2]/div/article/div[1]/div/@style')
        img_list = [img_url.replace("background-image:url(", "").replace(")","") for img_url in img_list]
    #     new_img_list = ["http://www.securitylab.ru" + img for img in img_list]
    #     print(img_list)
    #     # # 正文中图片替换地址
    #     # new_img_list = rename_image_name(img_list)
    #     # print(new_img_list)
    #     # 替换原始src地址为本地minio地址
    #     content_l = repair_content(content_l, img_list, SRC_REPLACE_PATH)
    #     print(content_l)
    #     # content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["content"] = content_l
        items["first_icon"] = ''

        if img_list:
            for index, img_url in enumerate(img_list):
                img_item = ImgproItem()
                img_name = img_url.split("/")[-1]
                img_item["img_name"] = img_name
                if index == 0:
                    items["first_icon"] = SRC_REPLACE_PATH + "/" + img_name
                img_item["minio_name"] = MINIO_PATH + img_name
                img_item["img_src"] = img_url
                img_item["bucket"] = MINIO_BUCKET
                img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
                print(97, img_item)
                yield img_item
        print(items)
        yield items