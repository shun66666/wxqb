import os
import re
import logging

import requests
import scrapy
from lxml import etree
from lxml.html import tostring

from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import SRC_REPLACE_PATH, MINIO_PATH, MINIO_BUCKET, IMAGES_STORE
from scrapy_sprider_project.tools.basic_tools import repair_content, getdate, rename_image_name, delete_script_content


class HkjsSpiderSpider(scrapy.Spider):
    name = 'hkjs_spider'
    allowed_domains = ['www.hackdig.com']
    start_urls = ['https://www.hackdig.com/']

    def start_requests(self):

        proxy = "http://127.0.0.1:7890"
        # tt = get_time()
        # ts = get_time_stamp()
        # url = "https://www.hackdig.com/"
        url = "http://www.hackdig.com/?cat-5.htm"
        # 允许重复抓取dont_filter设置为true
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_text = response.text
        element = etree.HTML(response_text)
        content_list = element.xpath('//div[@class="postList"]')
        for content_ele in content_list:
            items = BasicItem()
            title = content_ele.xpath('./h2/a/text()')[0].replace("\n", "").strip()
            target_url = content_ele.xpath('./h2/a/@href')[0].replace("\n", "").strip()
            summary = content_ele.xpath('./div[@class="listEntry"]/text()')[0].replace("\n", "").strip()
            time = content_ele.xpath('./div[@class="listDetal"]/span/text()')[0].replace("\n", "").strip()
            items["title"] = title
            items["summary"] = summary
            items["publish_time"] = time
            # date_yesterday = getdate(1)
            date_yesterday = getdate(4)
            if time:
                if date_yesterday > time[:10]:
                    break
            items["target_url"] = target_url
            print(f"报告来源：黑客技术,报告时间为{time},报告标题:{title}, 报告url：{items['target_url']},数据开始采集")
            # logging.log(f"报告来源：黑客技术, 报告时间：{time}, 报告title：{title}，报告url：{'target_url'}, 开始采集数据")
            yield scrapy.Request(
                    target_url,
                    dont_filter=True,
                    callback=self.parse_detail,
                    meta={"items": items},
                )
        # for i in range(1, 5):
        #     url = "http://www.hackdig.com/?cat-5.htm&p={str(i)}"
        #     yield scrapy.Request(url=url, callback=self.parse)

    def parse_detail(self, response):
        items = response.meta["items"]
        response_text = response.text
        element = etree.HTML(response_text)
        content_list = element.xpath('//*[@id="content"]')
        print(68, content_list)
        author = element.xpath('//*[@class="article-content js-article-content"]/@data-copyright-author')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        img_list = element.xpath('//*[@id="content"]//img/@src')
        img_list = [img_url for img_url in img_list if img_url.startswith("http://img403.hackdig.com/imgpxy.php?url=")]
        # print(65, img_list)
        img_list_new = [img_url.replace(r"http://img403.hackdig.com/imgpxy.php?url=", "")[::-1].replace("A3%", ":").replace("F2%", "/").replace("D3%", ".").replace("12%small", "") for img_url in img_list]
        img_list_new = [link_url.split(".png")[0]+".png" if ".png" in link_url else link_url for link_url in img_list_new]
        img_list_new = [link_url.split(".jpg")[0]+".jpg" if ".jpg" in link_url else link_url for link_url in img_list_new]
        img_list_new = [link_url.split(".jpeg")[0]+".jpeg" if ".jpeg" in link_url else link_url for link_url in img_list_new]
        if author:
            items["author"] = author[0]
        else:
            items["author"] = ""
        items["source_type"] = "黑客技术"
        for index, img_url in enumerate(img_list):
            if img_list_new[index].endswith("640F3%wx_fmt.png") or img_list_new[index].endswith("640F3%wx_fmt.jpeg") or img_list_new[index].endswith("640F3%wx_fmt.jpg"):
                img_list_new[index] = img_list_new[index].replace("/640F3%wx_fmt","")
                print(74, img_url, img_list_new[index])
            # content_l = re.sub(img_url, img_list_new[index], content_l)
            content_l = content_l.replace(img_url, img_list_new[index])
        # todo链接图片修改为本地服务器地址
        # print(78, content_l)
        content_l = repair_content(content_l, img_list_new, SRC_REPLACE_PATH)
        # print(79, content_l)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 1
        items["content"] = content_l
        # print(89, items)
        items["first_icon"] = ""
        for index, img_url in enumerate(img_list):
            img_item = ImgproItem()
            # 获取上一层目录
            # parPath = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
            img_name = img_list_new[index].split("/")[-1]
            # img_name = "/".join(img_list_new[index].split('/')[4:])
            img_item["img_name"] = img_name
            if index == 0:
                items["first_icon"] = SRC_REPLACE_PATH + "/" + img_name
            img_item["minio_name"] = MINIO_PATH + img_name
            img_item["img_src"] = img_list[index]
            img_item["bucket"] = MINIO_BUCKET
            img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
            yield img_item
        yield items

# url = "https://mmbiz.qpic.cn/mmbiz_png/rTicZ9Hibb6RW1bUG7iatQaMtBA4e6cjfnGmO4h6aCia0b30In9O4URNuqZfTMJrh7Z3dE0AiaNnTLAPwibUDFHN6Zfw/640F3%wx_fmt.png"
# print("/".join(url.split('/')[4:]))