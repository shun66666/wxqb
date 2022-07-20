import os

import logging
import scrapy
from lxml import etree
from lxml.html import tostring

from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime, getdate, tranforms_datetime2, \
    rename_image_name, repair_content, repair_content2, delete_script_content


class BleepingcomputerSpiderSpider(scrapy.Spider):
    name = 'bleepingcomputer_spider'
    allowed_domains = ['www.bleepingcomputer.com']
    start_urls = ['https://www.bleepingcomputer.com/']

    def start_requests(self):
        url = 'https://www.bleepingcomputer.com/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    # def start_requests(self):
    #     url = 'http://www.bleepingcomputer.com/'
    #     yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        # print(response_text)
        element = etree.HTML(response_text)
        author_list = element.xpath('//*[@id="bc-home-news-main-wrap"]/li/div[2]/ul/li[1]/a/text()')
        publish_time_list = element.xpath('//*[@id="bc-home-news-main-wrap"]/li/div[2]/ul/li[2]/text()')
        detail_time_list = element.xpath('//*[@id="bc-home-news-main-wrap"]/li/div[2]/ul/li[3]/text()')
        url_list = element.xpath('//*[@id="bc-home-news-main-wrap"]/li/div[2]/h4/a/@href')
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = element.xpath(f'//*[@id="bc-home-news-main-wrap"]/li[{index + 1}]/div[2]/h4/a/text()')[0].replace(
                "\n", "").strip()
            summary = element.xpath(f'//*[@id="bc-home-news-main-wrap"]/li[{index + 1}]/div[2]/p/text()')[0].replace(
                "\n", "").strip()
            author = author_list[index]
            origin_time = publish_time_list[index]
            origin_hms = detail_time_list[index]
            time = tranforms_datetime2(origin_time, origin_hms)
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：bleepingcomputer, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：bleepingcomputer, 报告时间：{time}, 报告title：{title}，报告url：{target_url}, 开始采集数据")
            items["publish_time"] = time
            items["title"] = title
            items["summary"] = summary
            items["author"] = author
            yield scrapy.Request(
                target_url,
                dont_filter=True,
                callback=self.parse_detail,
                meta={"items": items},
            )

    def parse_detail(self, response):
        items = response.meta["items"]
        response_text = response.text
        element = etree.HTML(response_text)
        items["source_type"] = "bleepingcomputer"
        # title = element.xpath('/html/body/main/div/h1/a/text()')[0].replace("\n", "").strip()
        content_list = element.xpath('//*[@class="articleBody"]')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        # print(content_l)
        img1_list = element.xpath('/html/body/div[1]/section[3]/div/div/div[1]/div/div[1]/div[2]/p/img/@src')
        img2_list = element.xpath('/html/body/div[1]/section[3]/div/div/div[1]/div/div[1]/div[2]/div/figure/img/@src')
        img3_list = [img_url for img_url in img2_list if img_url.startswith("https://www.bleepstatic.com")]
        img4_list = element.xpath('/html/body/div[1]/section[3]/div/div/div[1]/div/div[1]/div[2]/div/figure/img/@data-src')
        img_list = img1_list + img3_list + img4_list
        # img_list = img2_list + img3_list
        origin_img_list = img1_list + img2_list
        new_img_list = rename_image_name(img_list)
        content_l = repair_content2(content_l, new_img_list, origin_img_list,  SRC_REPLACE_PATH)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["content"] = content_l
        items["first_icon"] = ""
        # print(85, content_l)
        for index, img_url in enumerate(img_list):

            img_item = ImgproItem()
            img_name = new_img_list[index].split("/")[-1]
            img_item["img_name"] = img_name
            if index == 0:
                items["first_icon"] = SRC_REPLACE_PATH + "/" + img_name
            img_item["minio_name"] = MINIO_PATH + img_name
            img_item["img_src"] = img_url
            img_item["bucket"] = MINIO_BUCKET
            img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
            # print(93, img_item)
            yield img_item
        yield items