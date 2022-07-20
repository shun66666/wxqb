import os

import scrapy
from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import tranforms_datetime, getdate, rename_image_name, repair_content2, \
    delete_script_content


class SecurityaffairsSpiderSpider(scrapy.Spider):
    name = 'securityaffairs_spider'
    allowed_domains = ['securityaffairs.co']
    start_urls = ['http://securityaffairs.co/']

    def start_requests(self):
        url = 'http://securityaffairs.co/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        # print(response_text)
        element = etree.HTML(response_text)
        url_list = element.xpath('//div/div/div[2]/div/h3/a/@href')
        print(url_list)
        title_list = element.xpath('//div/div/div[2]/div/h3/a/text()')
        publish_time_list = element.xpath('//div/div/div[4]/a[1]/text()')
        author_list = element.xpath('//div/div/div[4]/a[2]/text()')
        summary_list = element.xpath('//div/div/div[3]/p/text()')
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index].replace("\n", "").strip()
            # target_url = element.xpath('./h2/a/@href')[0].replace("\n", "").strip()
            # time = element.xpath('./div[@class="listDetal"]/span/text()')[0].replace("\n", "").strip()
            items["title"] = title
            items["author"] = author_list[index]
            items["summary"] = summary_list[index]
            origin_time = publish_time_list[index]
            time = tranforms_datetime(origin_time)
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：securityaffairs, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：securityaffairs, 报告时间：{time}, 报告title：{title}，报告url：{'target_url'}, 开始采集数据")
            items["publish_time"] = time
            items["source_type"] = "securityaffairs"
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
        content_list = element2.xpath('//*[@id="content_wrapper"]/div/div/div[1]/div[3]/div[1]/div[1]/div')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        # img_list = element.xpath('/html/body/div[2]/div[4]/div[1]/div[1]/div/div/div/div[2]/div[1]/div/div[2]/a/div/img/@src')
        # 图片下载的原始地址
        img_list_ = element2.xpath('//div/div/div[1]/div[3]/div[1]/div[1]/div//figure/a/img/@src')
        # 去掉  ?resize=1024%2C577&ssl=1
        img_list = []
        for img_url in img_list_:
            if len(img_url.split(".png?")) > 1:
                img_url = img_url.split("?")[0]
                img_list.append(img_url)
        print(img_list)
        # 正文中图片替换地址
        new_img_list = rename_image_name(img_list)
        print(new_img_list)
        # 替换原始src地址为本地minio地址
        content_l = repair_content2(content_l, new_img_list, img_list, SRC_REPLACE_PATH)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["content"] = content_l
        items["first_icon"] = ""

        if img_list:
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