import re

import scrapy
import os

from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime, getdate, rename_image_name, repair_content2, \
    delete_script_content, repair_content


class SecuritylabSpiderSpider(scrapy.Spider):
    name = 'securitylab_spider'
    allowed_domains = ['www.securitylab.ru']
    start_urls = ['http://www.securitylab.ru/']

    def start_requests(self):
        url = 'http://www.securitylab.ru/news/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        # print(response_text)
        element = etree.HTML(response_text)
        url_last_list = element.xpath('//div[@class="col-lg-9"]/a/@href')
        url_list = ["http://www.securitylab.ru"+url for url in url_last_list]
        print(url_list)
        # title_list = element.xpath('//div[@class="col-lg-9"]/a/div/h2/font/font/text()')
        title_list = element.xpath('//div[@class="col-lg-9"]/a/div/h2//text()')
        print(title_list)
        publish_time_list = element.xpath('//div[@class="col-lg-9"]/a/div[2]/time/@datetime')
        print(publish_time_list)
        summary_list = element.xpath('//div[@class="col-lg-9"]/a/div[2]/p/text()')
        print(summary_list)
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index]
            items["title"] = title
            items["author"] = ""
            items["summary"] = summary_list[index]
            origin_time = publish_time_list[index]
            time = origin_time
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：securitylab, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            items["publish_time"] = time[:10]+" " + time[11:19]
            print(time[:10] +" "+time[11:19])
            items["source_type"] = "securitylab"
            yield scrapy.Request(
                target_url,
                dont_filter=True,
                callback=self.parse_detail,
                meta={"items": items},
            )


    def parse_detail(self, response):
        items = response.meta["items"]
        target_url = items["target_url"]
        id = target_url.split("/")[-1].split(".")[0]
        response_text = response.text
        element2 = etree.HTML(response_text)
        content_list = element2.xpath(f'//*[@id="article_{id}"]/div/div[2]/div[1]/div[1]/sape_index')
        author = element2.xpath(f'//*[@id="article_{id}"]/div/div[2]/div[1]/div[1]/sape_index/div[2]/text()')[0]
        print(author)
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        content_l = re.sub(r'.*?(div itemprop="headline" class="d-none">(.|\n)*?</div>)', "", content_l)
        print(content_l)
        img_list = element2.xpath(f'//*[@id="article_{id}"]/div/div[2]/div[1]/div[1]/sape_index/img/@src')
        new_img_list = ["http://www.securitylab.ru"+img for img in img_list]
        print(img_list)
        # # 正文中图片替换地址
        # new_img_list = rename_image_name(img_list)
        # print(new_img_list)
        # 替换原始src地址为本地minio地址
        content_l = repair_content(content_l, img_list, SRC_REPLACE_PATH)
        print(content_l)
        # content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["content"] = content_l

        items["first_icon"] = ""
        if img_list:
            for index, img_url in enumerate(new_img_list):
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
        # print(items)
        yield items




