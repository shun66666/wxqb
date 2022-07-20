# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import os
import time

from itemadapter import ItemAdapter
from minio import Minio
from minio.error import MinioException
from scrapy.exporters import JsonLinesItemExporter
from scrapy.pipelines.images import ImagesPipeline
import scrapy
import pymysql
from twisted.enterprise import adbapi
from scrapy_sprider_project.items import BasicItem, ImgproItem
from scrapy_sprider_project.tools.basic_tools import download_img
from scrapy_sprider_project.tools.minio_tool import MinioOperate


class JsonfileProjectPipeline:
    print(time.time(), "JsonfileProjectPipeline")

    def open_spider(self, spider):
        print("爬虫开始了！")

    def close_spider(self, spider):
        print("爬虫结束了...")

    def process_item(self, item, spider):
        # print(666, item)
        # 在setting配置了多个不同的管道按照优先级来本地化存储  如果这里包含return item则会在下一个优先级渠道上继续进行其他形式存储
        return item

class ImgsPipLine(ImagesPipeline):
    print(time.time(), "ImgsPipLine")

    def get_media_requests(self, item, info):
        # print(41, item)
        if isinstance(item, ImgproItem):
            # print(999)
            img_src = item['img_src']
            if img_src.endswith(".png") or item['img_src'].endswith(".jpg") or item['img_src'].endswith(".jpeg") or item['img_src'].endswith(".gif"):
                yield scrapy.Request(url=item['img_src'], meta={'item': item})
            elif img_src.startswith('http://img403.hackdig.com/imgpxy.php?url=gnp') or img_src.startswith(
                    'http://img403.hackdig.com/imgpxy.php?url=gpj') or img_src.startswith(
                'http://img403.hackdig.com/imgpxy.php?url=gepj'):
                yield scrapy.Request(url=item['img_src'], meta={'item': item})
            elif img_src.startswith('https://secure.gravatar.com'):
                yield scrapy.Request(url=item['img_src'], meta={'item': item})
            else:
                # print(66666, item['img_src'])
                download_img(item['img_src'], item["img_file_path"])
                # return item
        return item

    # 返回图片名称即可
    def file_path(self, request, item, response=None, info=None):
        item = request.meta['item']
        filePath = item['img_name']
        return filePath

    def item_completed(self, results, item, info):
        if isinstance(item, ImgproItem):
            minio_client = MinioOperate()
            bucket = item["bucket"]
            file_name = item["minio_name"]
            image_file_path = item["img_file_path"]
            file_directory = os.path.dirname(image_file_path)
            if not os.path.exists(file_directory):
                os.makedirs(file_directory)
            if os.path.exists(image_file_path):
                flag = minio_client.exist_object(bucket, file_name)
                if not flag:
                    print(f"开始上传文件：{file_name}")
                    minio_client.fput_object(bucket, file_name, image_file_path)
                    print(f'文件{file_name} 上传成功')
                    try:
                        pass
                        # 上传成功后删除本地的文件
                        os.remove(image_file_path)
                    except Exception as e:
                        print(e)
        return item


class MinioPipLine(object):
    print(time.time(), "MinioPipeline")

    def __init__(self, minio_client):
        self.minio_client = minio_client

    @classmethod
    def from_settings(cls, setting):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        cls.minio_client = Minio(setting['MINIO_HOST'],
                                 access_key=setting['MINIO_ACCESS_KEY'],
                                 secret_key=setting['MINIO_SECRET_KEY'],
                                 secure=False)
        return cls.minio_client

    def create_bucket(self, bucket):
        """
        1、先检查minio bucket是否存在，存在则返回True
        2、再通过client调用make_bucket
        3、创建成功则返回True，否则返回False
        :param bucket: String
        :return: bool
        """
        try:
            if self.minio_client.bucket_exists(bucket):
                return True
            self.minio_client.make_bucket("images")
        except MinioException as err:
            print(err)
            return False
        except ValueError as val_err:
            print(val_err)
            return False

    def bucket_exist(self, bucket):
        """
        判断bucket是否存在,存在返回True， 不存在返回False
        """
        self.minio_client.bucket_exists(bucket)

    def delete_bucket(self, bucket):
        """
        删除minio中bucket
        :param bucket: bucket name
        :return: bool
        """
        try:
            if not self.minio_client.bucket_exists(bucket):
                print("桶子不存在")
                return False
            self.minio_client.remove_bucket(bucket)
            return True
        except ValueError:
            return False

    def fget_object(self, bucket, object_name, file_name):
        self.minio_client.fget_object(
            bucket, object_name, file_name)

    def fput_object(self, bucket, object_name, file_name):
        self.minio_client.fput_object(
            bucket, object_name, file_name)

    def exist_object(self, bucket, object_name):
        # Get a full object.
        try:
            data = self.minio_client.get_object(bucket, object_name)
            if data:
                print(f"图片{object_name}已存在")
                return 1
            else:
                print(data)
                return 0
        except Exception as err:
            print(err)
            return 2


class MysqlPipeline(object):
    print(time.time(), "MysqlPipeline")

    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):  # 函数名固定，会被scrapy调用，直接可用settings的值
        """
        数据库建立连接
        :param settings: 配置参数
        :return: 实例化参数
        """
        adbparams = dict(
            host=settings['MYSQL_HOST'],
            port=settings['MYSQL_PORT'],
            db=settings['MYSQL_DBNAME'],
            user=settings['MYSQL_USER'],
            password=settings['MYSQL_PASSWORD'],
            charset='utf8mb4',
            cursorclass=pymysql.cursors.DictCursor  # 指定cursor类型
        )
        # 连接数据池ConnectionPool，使用pymysql或者Mysqldb连接
        dbpool = adbapi.ConnectionPool('pymysql', **adbparams)
        print("连接成功")
        # 返回实例化参数
        return cls(dbpool)

    def process_item(self, item, spider):
        """
        使用twisted将MySQL插入变成异步执行。通过连接池执行具体的sql操作，返回一个对象
        """
        if isinstance(item, BasicItem):
            query = self.dbpool.runInteraction(self.do_insert, item)  # 指定操作方法和操作数据
            # 添加异常处理
            query.addCallback(self.handle_error)  # 处理异常
            return item

    def do_insert(self, cursor, item):
        # 对数据库进行插入操作，并不需要commit，twisted会自动commit
        insert_sql = """
        insert into hl_public_report(title,summary,author,publish_time,content,target_url,source_type,first_icon,state,translate_state) VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    """
        if len(item['summary']) >= 1000:
            item['summary'] = item['summary'][:1000]
        cursor.execute(insert_sql, (item['title'], item['summary'], item['author'], item['publish_time'],
                                    item['content'], item['target_url'], item['source_type'], item['first_icon'], 3, item['translate_state']))
        print(f"报告来源：item['source_type'], 报告时间：{item['publish_time']}, 报告标题：{item['title']}, 报告url：{item['target_url']}, 数据入库完成")

    def handle_error(self, failure):
        if failure:
            # 打印错误信息
            print(failure)
