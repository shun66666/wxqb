import os


import scrapy
from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime, getdate, repair_content2, rename_image_name, \
    delete_script_content


class ItsecurityguruSpiderSpider(scrapy.Spider):
    name = 'itsecurityguru_spider'
    allowed_domains = ['www.itsecurityguru.org']
    start_urls = ['https://www.itsecurityguru.org/']

    def start_requests(self):
        url = 'https://www.itsecurityguru.org/news/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        element = etree.HTML(response_text)
        publish_time_list = element.xpath('/html/body/div[2]/div[4]/div/div[1]/div/div/div/div[4]/div/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div/article/div[2]/div/div/a/text()')
        url_list = element.xpath('/html/body/div[2]/div[4]/div/div[1]/div/div/div/div[4]/div/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div/article/div[2]/h3/a/@href')
        title_list = element.xpath('/html/body/div[2]/div[4]/div/div[1]/div/div/div/div[4]/div/div[1]/div/div/div/div/div/div/div/div/div[1]/div[1]/div/article/div[2]/h3/a/text()')
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index].replace("\n", "").strip()
            # target_url = element.xpath('./h2/a/@href')[0].replace("\n", "").strip()
            # time = element.xpath('./div[@class="listDetal"]/span/text()')[0].replace("\n", "").strip()
            items["title"] = title
            items["summary"] = ""
            origin_time = publish_time_list[index]
            time = tranforms_datetime(origin_time)
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：itsecurityguru, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：itsecurityguru, 报告时间：{time}, 报告title：{title}，报告url：{'target_url'}, 开始采集数据")
            items["publish_time"] = time
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
        # title = element.xpath('/html/body/main/div/h1/a/text()')[0].replace("\n", "").strip()
        # target_url = element.xpath('./h2/a/@href')[0].replace("\n", "").strip()
        # summary = element.xpath('./div[@class="listEntry"]/text()')[0].replace("\n", "").strip()
        # time = element.xpath('//*[@id="Blog1"]/div/div/div/div[4]/div/span[1]/text()')[0].replace("\n", "").strip()
        author = element2.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[1]/div/div/div[1]/div[1]/a/text()')[0].replace("\n", "").strip()
        items["source_type"] = "itsecurityguru"
        content_list = element2.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div/div/div/div[2]/div[1]/div')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        # img_list = element.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[2]/a/div/img/@src')
        # 图片下载的原始地址
        img_list = element2.xpath('//div[@class="thumbnail-container animate-lazy"]/img/@data-src')
        # 被替换src的url
        src_list = element2.xpath('//div[@class="thumbnail-container animate-lazy"]/img/@src')
        # 正文中图片替换地址
        new_img_list = rename_image_name(img_list)
        # 替换原始src地址为本地minio地址
        content_l = repair_content2(content_l, new_img_list, src_list, SRC_REPLACE_PATH)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["content"] = content_l
        items["author"] = author

        # print(80, img_list)
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
            # print(91, img_item)
            yield img_item
        # print(items)
        items["first_icon"] = ""
        yield items