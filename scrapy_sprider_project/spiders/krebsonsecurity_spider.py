import os

import scrapy
from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime, getdate, getTime, rename_image_name, \
    repair_content2, delete_script_content


class KrebsonsecuritySpiderSpider(scrapy.Spider):
    name = 'krebsonsecurity_spider'
    allowed_domains = ['krebsonsecurity.com']
    start_urls = ['https://krebsonsecurity.com/']

    def start_requests(self):
        url = 'https://krebsonsecurity.com/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        element = etree.HTML(response_text)
        title_list = element.xpath('//article/header/h2/a/text()')
        publish_time_list = element.xpath('//header/div[2]/div/div[1]/span/text()')
        main_element = element.xpath('//*/article')
        url_list = element.xpath('//header/h2/a/@href')
        for index, content_element in enumerate(main_element):
            items = BasicItem()
            title = title_list[index].replace("\n", "").strip()
            items['title'] = title
            items['summary'] = ''
            items['author'] = ''
            origin_time = publish_time_list[index].strip()
            content_list = content_element.xpath('./div')
            # content_text = content_element.xpath('./div//text()')
            # print(29, content_text)
            content_l = tostring(content_list[0], encoding="utf-8").decode()
            img_list = content_element.xpath('.//img/@src')
            # 正文中图片替换地址
            new_img_list = rename_image_name(img_list)
            # 替换原始src地址为本地minio地址
            content_l = repair_content2(content_l, new_img_list, img_list, SRC_REPLACE_PATH)
            # print(31, content_l)
            time = tranforms_datetime(origin_time)
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            target_url = url_list[index]
            items['target_url'] = target_url
            items['publish_time'] = time
            items["source_type"] = "krebsonsecurity"
            content_l = delete_script_content(content_l)
            items["translate_state"] = 2
            items['content'] = content_l
            print(f"报告来源：krebsonsecurity, 报告时间：{time}, 报告title：{title}，报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：krebsonsecurity, 报告时间：{time}, 报告title：{title}，报告url：{target_url}, 开始采集数据")
            # print(items)
            yield scrapy.Request(
                target_url,
                dont_filter=True,
                callback=self.parse_detail,
                meta={"items": items},
            )

    def parse_detail(self, response):
        items = response.meta["items"]
        response_text = response.text
        element2 = etree.HTML(response_text)
        items["source_type"] = "krebsonsecurity"
        content_list = element2.xpath('//*[@id="content"]/article/div')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        # img_list = element.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[2]/a/div/img/@src')
        # 图片下载的原始地址
        img_list = element2.xpath('//*[@id="content"]/article/div/div/a/@href')
        # 被替换src的url
        src_list = element2.xpath('//*[@id="content"]/article/div/div/a/img/@src')
        # 正文中图片替换地址
        new_img_list = rename_image_name(img_list)
        # 替换原始src地址为本地minio地址
        content_l = repair_content2(content_l, new_img_list, src_list, SRC_REPLACE_PATH)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["content"] = content_l

        items["first_icon"] = ""
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
            # print(img_item)
            yield img_item
        # print(items)
        yield items





