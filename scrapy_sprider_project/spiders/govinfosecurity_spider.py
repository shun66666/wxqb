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

class GovinfosecuritySpiderSpider(scrapy.Spider):
    name = 'govinfosecurity_spider'
    allowed_domains = ['www.govinfosecurity.com']
    start_urls = ['http://www.govinfosecurity.com/']

    def start_requests(self):
        url = 'https://www.govinfosecurity.com/latest-news'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        # print(response_text)
        element = etree.HTML(response_text)
        url_list = element.xpath('//*[@id="latest-news-page"]/div[1]/article/div/div[2]/h2/a/@href')
        # url_list = ["http://www.securitylab.ru" + url for url in url_last_list]
        # print(len(url_list))
        title_list = element.xpath('//*[@id="latest-news-page"]/div[1]/article/div/div[2]/h2/a/text()')
        # print(len(title_list))
        author_list = element.xpath(
            '//*[@id="latest-news-page"]/div[1]/article/div/div[2]/p[1]/a/text()')
        # print(len(author_list))
        publish_time_list = element.xpath(
            '//*[@id="latest-news-page"]/div[1]/article/div/div[2]/p[1]/span[1]/text()')
        publish_time_list = [tranforms_datetime(publish_time) for publish_time in publish_time_list]
        summary_list = element.xpath(
            '//*[@id="latest-news-page"]/div[1]/article/div/div[2]/p[2]/text()')
        # print(summary_list)
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index]
            items["title"] = title
            items["author"] = author_list[index]
            items["summary"] = summary_list[index]
            origin_time = publish_time_list[index]
            time = origin_time
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：govinfosecurity, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            items["publish_time"] = time
            items["source_type"] = "govinfosecurity"
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
        content_list = element2.xpath('//div/article[@id="generic-article"]')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        content_l = re.search('.*(<article .*?>(.|\n)*?</article>).*', content_l).group(0)
        content_l = delete_script_content(content_l)
        content_l = re.sub(r'(<p class="text-muted">(.|\n)*?</div>)', "", content_l)
        content_l = re.sub(r'(<h1 class="article-title">(.|\n)*?</div>)', "", content_l)
        content_l = re.sub(r'(<span class="article-sub-title">(.|\n)*?</div>)', "", content_l)
        content_l = re.sub(r'(<span class="article-byline">(.|\n)*?</div>)', "", content_l)
        content_l = re.sub(r'(<div class="share-this-buttons ">(.|\n)*?</div>)', "", content_l)
        # content_l = "\n".join(
        #     [tostring(content, encoding="utf-8").decode().replace("\n", "") for content in content_list])
        img_list = element2.xpath(f'//*[@id="generic-article"]//img/@src')
        # print(img_list)
        content_l = repair_content(content_l, img_list, SRC_REPLACE_PATH)
        # print(content_l)
        items["translate_state"] = 2
        items["content"] = content_l
        img_name = img_list[0].split("/")[-1]
        items["first_icon"] = SRC_REPLACE_PATH + "/" + img_name
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
