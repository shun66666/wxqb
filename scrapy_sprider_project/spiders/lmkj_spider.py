import json

import scrapy
import logging
from scrapy_sprider_project.items import BasicItem
from scrapy_sprider_project.tools.basic_tools import getdate


class LmkjSpiderSpider(scrapy.Spider):
    name = 'lmkj_spider'
    allowed_domains = ['nti.nsfocus.com']
    url = 'https://nti.nsfocus.com/api/v2/apt/news/?query=&page={}'

    def start_requests(self):
        for i in range(1, 3):
            url = self.url.format(str(i))
            yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        response_dict = json.loads(response.text)
        # print("parse-->", response_dict["objects"])
        lm_infos = response_dict["objects"]
        for sig_info in lm_infos:
            items = BasicItem()
            time = sig_info.get("reported", "")[:10]
            date_yesterday = getdate(1)
            # date_yesterday = getdate(5)
            # print(32, date_yesterday, time)
            items["title"] = sig_info.get("title", "")
            items["target_url"] = sig_info.get("url")[0] if sig_info.get("url") else ""
            if date_yesterday > time:
                break
            print(
                f"报告来源：绿盟科技, 报告时间：{sig_info.get('reported')}, 报告标题：{items['title']}，报告url：{items['target_url']}, 开始采集数据")
            items["summary"] = sig_info.get("description", "").replace("\r", "").replace("\n", "")
            items["author"] = sig_info.get("created_by", "")
            # items["publish_time"] = sig_info.get("reported", "")
            items["publish_time"] = sig_info.get("reported")[:10] + " " + sig_info.get("reported")[11:19]
            items["content"] = sig_info.get("content", "")
            items["source_type"] = "绿盟科技"
            yield items
