# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapySpriderProjectItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class BasicItem(scrapy.Item):
    title = scrapy.Field()  # 报告的标题
    summary = scrapy.Field()  # 报告简介
    author = scrapy.Field()  # 报告的作者
    publish_time = scrapy.Field()  # 报告发布的时间
    content = scrapy.Field()  # 报告的正文
    target_url = scrapy.Field()  # 报告的源地址
    source_type = scrapy.Field()  # 报告的来源类别，诸如：freebuf，macfee
    first_icon = scrapy.Field()  # 把第一张图片作为封面
    translate_state = scrapy.Field()  # 2 表示待翻译
    # state = scrapy.Field()  # 0-已入库，1-已忽略，2-未完成
    # task_id = scrapy.Field()  # 报告可以生成一个对应的拓线分析的任务
    # sample_hash = scrapy.Field()  # 存放多个hash
    # url = scrapy.Field()  # 存放多个url
    # ip = scrapy.Field()  # 存放多个ip
    # email = scrapy.Field()  # 存放多个email
    # domain = scrapy.Field()  # 存放多个domain
    # sensitive_string = scrapy.Field()  # 存放多个sensitive_string
    # create_time = scrapy.Field()  # 创建时间
    # update_time = scrapy.Field()  # 最近一次的修改时间


class ImgproItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    img_src = scrapy.Field()
    img_name = scrapy.Field()
    bucket = scrapy.Field()
    img_file_path = scrapy.Field()
    minio_name = scrapy.Field()


class MinioItem(scrapy.Item):
    # define the fields for your item here like:
    bucket = scrapy.Field()
    file_name = scrapy.Field()
    img_file_path = scrapy.Field()




