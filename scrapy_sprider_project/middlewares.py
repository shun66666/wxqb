# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import asyncio
import base64
import logging
import time
from asyncio.log import logger
from functools import partial

from scrapy.http import HtmlResponse
from w3lib.http import basic_auth_header
from scrapy import signals
from scrapy.dupefilters import RFPDupeFilter
# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter

# from scrapy_sprider_project.settings import AROAY_CLOUDSCRAPER_DELAY, AROAY_CLOUDSCRAPER_DOWNLOAD_TIMEOUT, \
#     AROAY_CLOUDSCRAPER_LOGGING_LEVEL


class ScrapySpriderProjectSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class ScrapySpriderProjectDownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.
    print("mmysql")
    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        print(1)
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # print(97, response.status)
        # if response.status == 403:
        #     if spider.name == "bleepingcomputer_spider":
        #         url = request.url
        #         response = spider.scraper.get(url)
        #         time.sleep(5)
        #         # return HtmlResponse(url=url, body=req.text, encoding="utf-8", request=request)
        #         return response
        # print(2)
        return response

        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

# class ProxyMiddleware(object):
#     def process_request(self, request, spider):
#         # setup basic authentication for the proxy
#         proxy = "unmetered.residential.proxyrack.net:222"
#         # 固定写法
#         request.meta["proxy"] = 'http://' + proxy
#         premium.residential.rotating.proxyrack.net:10000 ip-api.com/json
#                            vpswote-country-US:6f4076-80e06b-e459f5-fe604d-ae99b4
#         proxy_user_pass = "vpswote-country-CN:6f4076-80e06b-e459f5-fe604d-ae99b4"
#         auth = base64.b64encode(bytes(proxy_user_pass, 'utf-8'))
#         # request.headers['Proxy-Authorization'] = basic_auth_header('vpswote-country-CN', '6f4076-80e06b-e459f5-fe604d-ae99b4','utf-8')
#         request.headers['Proxy-Authorization'] = b'Basic ' + auth


class BasicProxyMiddleware(object):
    def process_request(self, request, spider):
        # proxy = "socks5://127.0.0.1:7890"
        # proxy = "http://10.251.9.206:35921"
        proxy = "http://127.0.0.1:7890"
        request.meta["proxy"] = proxy
        print(f"TestProxyMiddleware --> {proxy}")


# class CloudScraperMiddleware(object):
#     """
#     Downloader middleware handling the requests with Puppeteer
#     """
#
#     def __init__(self):
#         self.scraper = cloudscraper.create_scraper(browser={
#             'browser': 'google',
#             'platform': 'windows',
#             'mobile': False
#         })
#
#     # 将cloudflare变为协程函数
#     def _block_get(self, url, *args, **kwargs):
#         response = self.scraper.get(url, *args, **kwargs)
#         # 返回response对象
#         return response
#
#     async def _simple_run_in_executor(self, f, *args, async_loop=None, **kwargs):
#         loopx = async_loop or asyncio.get_event_loop()
#         response = await loopx.run_in_executor(None, partial(f, *args, **kwargs))
#         return response
#
#     # f封装requests为协程函数
#     async def async_get(self, url, *args, **kwargs):
#         response = await self._simple_run_in_executor(self._block_get, url, *args, **kwargs)
#         return response
#
#     @classmethod
#     def from_crawler(cls, crawler):
#         """
#         init the middleware
#         :param crawler:
#         :return:
#         """
#         settings = crawler.settings
#         logging_level = settings.get('AROAY_CLOUDSCRAPER_LOGGING_LEVEL', AROAY_CLOUDSCRAPER_LOGGING_LEVEL)
#         logging.getLogger('websockets').setLevel(logging_level)
#         logging.getLogger('aroay_cloudscraper').setLevel(logging_level)
#         cls.download_timeout = settings.get('AROAY_CLOUDSCRAPER_DOWNLOAD_TIMEOUT',
#                                             settings.get('DOWNLOAD_TIMEOUT', AROAY_CLOUDSCRAPER_DOWNLOAD_TIMEOUT))
#         cls.delay = settings.get('AROAY_CLOUDSCRAPER_DELAY', AROAY_CLOUDSCRAPER_DELAY)
#         return cls()
#
#     async def _process_request(self, request, spider):
#         """
#         use aroay_cloudscraper to process spider
#         :param request:
#         :param spider:
#         :return:
#         """
#         # get aroay_cloudscraper meta
#         cloudscraper_meta = request.meta.get('aroay_cloudscraper') or {}
#         logger.debug('cloudscraper_meta %s', cloudscraper_meta)
#         if not isinstance(cloudscraper_meta, dict) or len(cloudscraper_meta.keys()) == 0:
#             return
#
#         # 设置代理
#         _proxy = cloudscraper_meta.get('proxy')
#         # logger.info("set proxy is %s" % _proxy)
#
#         # 设置请求超时
#         _timeout = self.download_timeout
#         if cloudscraper_meta.get('timeout') is not None:
#             _timeout = cloudscraper_meta.get('timeout')
#         _cookies = cloudscraper_meta.get('cookies ')
#
#         logger.debug('crawling %s', request.url)
#         response = await self.async_get(request.url, proxies=_proxy, timeout=_timeout,
#                                         cookies=_cookies)
#
#         # 设置延迟
#         _delay = self.delay
#         if cloudscraper_meta.get('delay') is not None:
#             _delay = cloudscraper_meta.get('delay')
#         if _delay is not None:
#             logger.debug('sleep for %ss', _delay)
#             await asyncio.sleep(_delay)
#
#         # 返回二进制
#         response = HtmlResponse(
#             request.url,
#             status=response.status_code,
#             headers=response.headers,
#             body=response.content,
#             encoding='utf-8',
#             request=request
#         )
#         return response
#
#     def process_request(self, request, spider):
#         """
#         process request using aroay_cloudscraper
#         :param request:
#         :param spider:
#         :return:
#         """
#         logger.debug('processing request %s', request)
#         return as_deferred(self._process_request(request, spider))
#
#     async def _spider_closed(self):
#         pass
#
#     def spider_closed(self):
#         """
#         callback when spider closed
#         :return:
#         """
#         return as_deferred(self._spider_closed())

