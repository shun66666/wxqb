import os
import logging
import scrapy
from lxml import etree
from lxml.html import tostring

from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import repair_content, tranforms_datetime, getdate, rename_image_name, \
    repair_content2, delete_script_content


class HackernewsSpiderSpider(scrapy.Spider):
    name = 'hackernews_spider'
    allowed_domains = ['thehackernews.com']
    start_urls = ['https://thehackernews.com/']


    def start_requests(self):
        url = 'https://thehackernews.com/'
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        element = etree.HTML(response_text)
        publish_time_list = element.xpath('//*[@id="Blog1"]/div[1]/div/a/div/div[2]/div[1]/text()')
        url_list = element.xpath('//*[@id="Blog1"]/div[1]/div/a/@href')
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = element.xpath(f'//*[@id="Blog1"]/div[1]/div[@class="body-post clear"]/a/div/div[2]/h2/text()')[index].replace("\n", "").strip()
            # target_url = element.xpath('./h2/a/@href')[0].replace("\n", "").strip()
            summary = element.xpath(f'//*[@id="Blog1"]/div[1]/div[@class="body-post clear"]/a/div/div[2]/div[2]/text()')[index].replace("\n", "").strip()
            # time = element.xpath('./div[@class="listDetal"]/span/text()')[0].replace("\n", "").strip()
            items["title"] = title
            items["summary"] = summary
            origin_time = publish_time_list[index]
            time = tranforms_datetime(origin_time)
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：thetracknews, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：thetracknews, 报告时间：{time}, 报告title：{title}，报告url：{target_url}, 开始采集数据")
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
        element = etree.HTML(response_text)
        title = element.xpath('/html/body/main/div/h1/a/text()')[0].replace("\n", "").strip()
        # target_url = element.xpath('./h2/a/@href')[0].replace("\n", "").strip()
        # summary = element.xpath('./div[@class="listEntry"]/text()')[0].replace("\n", "").strip()
        time = element.xpath('//*[@id="Blog1"]/div/div/div/div[4]/div/span[1]/text()')[0].replace("\n", "").strip()
        author = element.xpath('//*[@id="Blog1"]/div/div/div/div[4]/div/span[2]/a/text()')[0].replace("\n", "").strip()
        items["title"] = title
        # items["summary"] = summary
        items["publish_time"] = tranforms_datetime(time)
        items["author"] = author
        items["source_type"] = "thetrackernews"
        content_list = element.xpath('//*[@id="articlebody"]')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        img_list = element.xpath('//*[@id="articlebody"]/div/a/img/@src')
        # img2_list = element.xpath('//*[@id="articlebody"]/div/a/img/@data-src')
        # todo链接图片修改为本地服务器地址
        # 这里面href的一个层级s728-e100和src不一样s728-e1000
        new_img_list = rename_image_name(img_list)
        content_l = repair_content2(content_l, new_img_list, img_list, SRC_REPLACE_PATH)
        # print(content_l)
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
            yield img_item
        yield items

