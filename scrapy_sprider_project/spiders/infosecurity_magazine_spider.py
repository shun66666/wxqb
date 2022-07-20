
import scrapy
from lxml import etree
from lxml.html import tostring
import logging
from scrapy_sprider_project.items import BasicItem
from scrapy_sprider_project.tools.basic_tools import getdate, delete_script_content


class InfosecurityMagazineSpiderSpider(scrapy.Spider):
    name = 'infosecurity_magazine_spider'
    allowed_domains = ['www.infosecurity-magazine.com']
    start_urls = ['https://www.infosecurity-magazine.com/']

    def parse(self, response):
        url = 'https://www.infosecurity-magazine.com/'
        # self.scraper = cloudscraper.create_scraper()
        yield scrapy.Request(url=url, callback=self.parse, dont_filter=True)

    def parse(self, response):
        # 翻页问题
        response_text = response.text
        # print(19, response_text)
        element = etree.HTML(response_text)
        url_list = element.xpath('//*[@id="pnlMainContent"]/div[2]/div[2]/div/div/a/@href')
        title_list = element.xpath('//*[@id="pnlMainContent"]/div[2]/div[2]/div/div/a//h3/text()')
        publish_time_list = element.xpath('//*[@id="pnlMainContent"]/div[2]/div[2]/div/div/a//div/time/@datetime')
        for index, target_url in enumerate(url_list):
            items = BasicItem()
            items['target_url'] = target_url
            title = title_list[index]
            publish_time = publish_time_list[index]
            time = publish_time[:10] + " " + publish_time[11:19]
            date_yesterday = getdate(1)
            date_yesterday = getdate(5)
            if date_yesterday > time[:10]:
                break
            print(f"报告来源：security_magazine, 报告时间：{time}, 报告标题：{title}, 报告url：{target_url}, 开始采集数据")
            # logging.log(f"报告来源：security_magazine, 报告时间：{time}, 报告title：{title}，报告url：{'target_url'}, 开始采集数据")
            items["publish_time"] = time
            items["title"] = title
            # items["author"] = author
            # items["summary"] = summary
            print(items)
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
        items["source_type"] = "security_magazine"
        content_list = element.xpath('//*[@id="layout-"]/p')
        # content_list = element.xpath('//*[@id="cphContent_pnlMainContent"]')
        author = element.xpath('//*[@id="cphContent_pnlMainContent"]/div[1]/h4/a/text()')
        summary = " ".join(element.xpath('//*[@id="layout-"]/p[1]//text()'))
        content_l = "\n".join([tostring(content, encoding="utf-8").decode().replace("\n", "") for content in content_list])
        print(60, content_l)
        content_l = delete_script_content(content_l)
        items["translate_state"] = 2
        items["author"] = author
        items["summary"] = summary
        items['content'] = content_l
        items["first_icon"] = ''
        yield items




"""
支持sock5代理
"""