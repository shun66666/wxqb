import json
import os
import time
# import logging
import scrapy
from lxml import etree
from lxml.etree import tostring

from ..items import BasicItem, ImgproItem, MinioItem
from ..settings import SRC_REPLACE_PATH, MINIO_BUCKET, IMAGES_STORE, MINIO_PATH
from ..tools.basic_tools import get_time, get_time_stamp, repair_content, getdate, rename_image_name, \
    delete_script_content


class AnquankeSpiderSpider(scrapy.Spider):
    name = 'anquanke_spider'
    # allowed_domains = ['www.anquanke.com', 'https://p3.ssl.qhimg.com']
    url = "https://www.anquanke.com/webapi/api/home/articles?category=&postDate={}&pageSize=10&_={}"

    def start_requests(self):
        tt = get_time()
        ts = get_time_stamp()
        url = self.url.format(str(tt), str(ts))
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        basic_url = "https://www.anquanke.com"
        response_dict = json.loads(response.text)
        # print("parse-->", response_dict["objects"])
        lm_infos = response_dict["data"]
        for sig_info in lm_infos:
            items = BasicItem()
            items["title"] = sig_info.get("title", "")
            items["summary"] = sig_info.get("desc", "").replace("\r", "").replace("\n", "")
            items["author"] = sig_info.get("author", "")
            time = sig_info.get("time", "")
            # date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            # 该报告时间超过昨天表示为过期情报不需要重复爬取
            if time:
                if date_yesterday > time[:10]:
                    break
            items["publish_time"] = time
            items["content"] = sig_info.get("content", "")
            items["target_url"] = basic_url + sig_info.get("url")
            items["source_type"] = "安全客"
            # items["state"] = sig_info.get("state", "")
            # items["task_id"] = sig_info.get("task_id", "")
            # items["sample_hash"] = sig_info.get("sample_hash", [])
            # items["url"] = []
            # items["ip"] = sig_info.get("ip", [])
            # items["email"] = sig_info.get("email", [])
            # items["domain"] = sig_info.get("domain", [])
            # items["sensitive_string"] = sig_info.get("sensitive_string", [])
            # items["create_time"] = sig_info.get("time", "")
            # items["update_time"] = sig_info.get("time", "")
            # items.extend(response_dict["objects"])
            print(f"报告来源：安全客, 报告时间：{time}, 报告title：{sig_info.get('title', '')}，报告url：{items['target_url']}, 开始采集数据")
            # logging.WARNING(f"报告来源：安全客, 报告时间：{time}, 报告title：{sig_info.get('title', '')}，报告url：{items['target_url']}, 开始采集数据")
            yield scrapy.Request(
                items["target_url"],
                callback=self.parse_detail,
                meta={"items": items}
                , dont_filter=True
            )
            # 如需要则爬取下一页
            if time:
                if date_yesterday <= str(time)[:10]:
                    tt = time[:10]
                    ts = get_time_stamp()
                    url = self.url.format(tt, str(ts))
                    yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)
                else:
                    break
            else:
                break

    def parse_detail(self, response):
        items = response.meta["items"]
        response_text = response.text
        element = etree.HTML(response_text)
        linklist = element.xpath('/html/body/main/div/div/div[1]/div[1]/div[2]/p/img/@data-original')
        linklist = [link_url for link_url in linklist if
                    link_url.endswith(".png") or link_url.endswith(".jpg") or link_url.endswith(".jpeg")]
        content_list = element.xpath('/html/body/main/div/div/div[1]/div[1]/div[2]')
        content_l = tostring(content_list[0], encoding="utf-8").decode()
        content = "".join([s for s in content_l.splitlines(True) if s.strip()])
        # 需要将图片地址的前缀换成本地路径,原图片名称太短进行重命名
        new_linklist = rename_image_name(linklist)
        content = repair_content(content, new_linklist, SRC_REPLACE_PATH)
        content_l = delete_script_content(content)
        items["content"] = content_l
        items["translate_state"] = 1
        items["first_icon"] = ''
        for index, download_url in enumerate(linklist):
            img_item = ImgproItem()
            img_name = new_linklist[index].split("/")[-1]
            img_item["img_src"] = download_url
            img_item["img_name"] = img_name
            if index == 0:
                items["first_icon"] = SRC_REPLACE_PATH + "/" + new_linklist[0].split("/")[-1]
            img_item["minio_name"] = MINIO_PATH + img_name
            img_item["bucket"] = MINIO_BUCKET
            img_item["img_file_path"] = os.path.join(IMAGES_STORE, img_name)
            yield img_item
        yield items  # 返回生成文件
