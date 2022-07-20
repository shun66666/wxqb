import json
import os
import re

import scrapy
import logging

from lxml import etree

from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.settings import MINIO_PATH, MINIO_BUCKET, IMAGES_STORE, SRC_REPLACE_PATH
from scrapy_sprider_project.tools.basic_tools import getdate, is_scrapy_flag, repair_content, rename_image_name, \
    delete_script_content

logger = logging.getLogger(__name__)


class AnhengSpiderSpider(scrapy.Spider):
    name = 'anheng_spider'
    # allowed_domains = ['ti.dbappsecurity.com.cn']
    start_urls = ['http://ti.dbappsecurity.com.cn/']

    def start_requests(self):
        # tt = get_time()
        # ts = get_time_stamp()
        # url = "https://ti.dbappsecurity.com.cn/info"
        url = "https://ti.dbappsecurity.com.cn/web/info/page"
        payload = {"page": 1, "size": 10}
        # 允许重复抓取dont_filter设置为true
        headers = {
            'Content-Type': 'application/json',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.127 Safari/537.36'
        }
        yield scrapy.Request(url, method="POST", body=json.dumps(payload), headers=headers, callback=self.parse, dont_filter=True)
        # yield scrapy.FormRequest(url=url, headers=headers, formdata=payload, callback=self.parse, dont_filter=True)
        # yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_dict = json.loads(response.text)
        lm_infos = response_dict["data"]["data"]
        for sig_info in lm_infos:
            items = BasicItem()
            origin_time = sig_info.get("creatTime", "")[:10]
            date_yesterday = getdate(1)
            items["title"] = sig_info.get("title", "")
            items["summary"] = sig_info.get("description", "")
            items["author"] = sig_info.get("authorName", "")
            if date_yesterday > origin_time:
                break
            time = sig_info.get("creatTime")[:10] + " " + sig_info.get("creatTime")[11:19]
            target_url = "https://ti.dbappsecurity.com.cn/web/info/"+str(sig_info.get("id"))
            items["target_url"] = target_url
            print(f"报告来源：安恒威胁情报中心, 报告时间：{time}, 报告标题：{items['title']}，报告url：{target_url}, 开始采集数据")
            items["publish_time"] = str(time)
            content = sig_info.get("content", "")
            image_list = re.findall(".*src=\"(.*?)\".*", content)
            items["source_type"] = "安恒威胁情报中心"
            items["first_icon"] = ''
            yield items
            image_list = ["http://ti.dbappsecurity.com.cn/" + image_url for image_url in image_list]
            new_image_list = rename_image_name(image_list)
            content_l = repair_content(content, new_image_list, SRC_REPLACE_PATH)
            content_l = delete_script_content(content_l)
            items["content"] = content_l
            items["translate_state"] = 1
            for index, download_url in enumerate(image_list):
                img_item = ImgproItem()
                img_item["img_src"] = download_url

                img_name = new_image_list[index].split("/")[-1]
                img_item["img_name"] = img_name
                img_item["minio_name"] = MINIO_PATH + img_name
                img_item["bucket"] = MINIO_BUCKET
                img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
                yield img_item

    # def parse(self, response):
    #     basic_url = "https://ti.dbappsecurity.com.cn"
    #     response_text = response.text
    #     # print(response_text)
    #     element = etree.HTML(response_text)
    #     # 抓取概览页面分页情况
    #     content_list = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[1]/div[2]/div[2]/div[@class="info-item"]')
    #     for content_ele in content_list:
    #         items = BasicItem()
    #         title = content_ele.xpath("./div/a/text()")[0].replace("\n", "").strip()
    #         url_suffix = content_ele.xpath("./div/a/@href")[0].replace("\n", "").strip()
    #         time = content_ele.xpath("./div/div/span[1]/text()")[0].replace("\n", "").strip()
    #         # flag = is_scrapy_flag(1, time)
    #         # if not flag:
    #         #     break
    #         # 剔除过期信息采集
    #         if "小时" or "分钟" or "秒" or "一天前" in time:
    #             pass
    #         else:
    #             print(time, "属于过期数据不采集")
    #             break
    #         if title.find("安全威胁情报周报") == -1:
    #             items["title"] = title
    #             target_url = basic_url+url_suffix
    #             items['target_url'] = target_url
    #             print(f"报告来源：安恒信息, 报告时间：{time}, 报告title：{title}，报告url：{target_url}, 开始采集数据")
    #             yield scrapy.Request(
    #                 target_url,
    #                 dont_filter=True,
    #                 callback=self.parse_content,
    #                 meta={"items": items}
    #             )
    #
    #
    # def parse_content(self, response):
    #     items = response.meta["items"]
    #     response_text = response.text
    #     # print(response_text)
    #     element = etree.HTML(response_text)
    #     # 获取概览，作者，发布时间以及目标源url，content是否需要获取
    #     author = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[1]/div/a[2]/text()')[0].replace("\n", "").strip()
    #     time = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[1]/div/span[1]/text()')[0].replace("\n", "").strip()
    #     url = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[3]/a/text()')
    #     if not url:
    #         url = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[4]/a/text()')
    #     content = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[2]//text()')
    #     if not content:
    #         # content = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[2]/div/span/text()')
    #         content = element.xpath('//*[@id="__layout"]/div/main/div/div[1]/div[2]/div[1]/div[1]/div/div[2]//text()')
    #     items["summary"] = "".join(content).replace("\n", "").strip()
    #     items["author"] = author
    #     items["publish_time"] = time
    #     items["content"] = ""
    #     if url:
    #         items["target_url"] = url[0].replace("\n", "").strip()
    #     items["source_type"] = "安恒信息"
    #     # items["state"] = ""
    #     # items["task_id"] = ""
    #     # items["sample_hash"] = sig_info.get("sample_hash", [])
    #     # items["url"] = [url.replace("\n", "").strip() for url in target_url if url]
    #     # items["ip"] = sig_info.get("ip", [])
    #     # items["email"] = sig_info.get("email", [])
    #     # items["domain"] = sig_info.get("domain", [])
    #     # items["sensitive_string"] = sig_info.get("sensitive_string", [])
    #     # items["create_time"] = sig_info.get("time", "")
    #     # items["update_time"] = sig_info.get("time", "")
    #     yield items
