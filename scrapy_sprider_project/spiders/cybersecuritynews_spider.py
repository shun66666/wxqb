import os

import logging
import scrapy
from lxml import etree
from lxml.html import tostring

from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import MINIO_PATH, MINIO_BUCKET, IMAGES_STORE, SRC_REPLACE_PATH
from scrapy_sprider_project.tools.basic_tools import getdate, rename_image_name, repair_content2, delete_script_content

"""
不能使用sock5代理
"""
class CybersecuritynewsSpiderSpider(scrapy.Spider):
    name = 'cybersecuritynews_spider'
    allowed_domains = ['cybersecuritynews.com']
    start_urls = ['http://cybersecuritynews.com/']

    def start_requests(self):
        url = 'https://cybersecuritynews.com/'
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        # 翻页问题
        response_text = response.text
        # print(19, response_text)
        element = etree.HTML(response_text)
        url_list = element.xpath('//*[@id="tdi_18"]/div/div/div[2]/h3/a/@href')
        title_list = element.xpath('//*[@id="tdi_18"]/div/div/div[2]/h3/a/text()')
        publish_time_list = element.xpath('//*[@id="tdi_18"]/div/div/div[2]/div[1]/span[2]/time/@datetime')
        author_list = element.xpath('//*[@id="tdi_18"]/div/div/div[2]/div[1]/span[1]/a/text()')
        summary_list = element.xpath('//*[@id="tdi_18"]/div/div/div[2]/div[2]/text()')
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index]
            publish_time = publish_time_list[index]
            time = publish_time[:10] + " " + publish_time[11:19]
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            print(date_yesterday, time)
            author = author_list[index]
            summary = summary_list[index]
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：cybersecuritynews, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：cybersecuritynews, 报告时间：{time}, 报告title：{title}，报告url：{target_url}, 开始采集数据")
            items["publish_time"] = time
            items["title"] = title
            items["author"] = author
            items["summary"] = summary
    #         print(items)
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
        items["source_type"] = "cybersecuritynews"
        # content_list = element.xpath('//article/div[2]/div[1]/div/div[4]')
        content_list = element.xpath('//article/div[2]/div[1]/div')
        # print(content_list)
        content_ele = content_list[0]
        img_list = content_ele.xpath('.//img/@src')
        # print(66, img_list)
        # todo 修改正文中src的地址
        new_img_list = rename_image_name(img_list)
        # print(new_img_list)
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        content_l = repair_content2(content_l, new_img_list, img_list, SRC_REPLACE_PATH)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items['content'] = content_l

        for index, download_url in enumerate(img_list):
            img_item = ImgproItem()
            img_name = download_url.split("/")[-1]
            img_item["img_src"] = download_url
            if img_name.endswith(".png") or img_name.endswith(".jpg") or img_name.endswith(".jpeg"):
                pass
            else:
                img_name = img_name+".jpeg"
            img_item["img_name"] = img_name
            if index == 0:
                items["first_icon"] = SRC_REPLACE_PATH + "/" + img_name
            img_item["minio_name"] = MINIO_PATH + img_name
            img_item["bucket"] = MINIO_BUCKET
            img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
            # print(img_item)
            yield img_item
        # print(items)
        yield items