# Scrapy settings for scrapy_sprider_project project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import logging
BOT_NAME = 'scrapy_sprider_project'

SPIDER_MODULES = ['scrapy_sprider_project.spiders']
NEWSPIDER_MODULE = 'scrapy_sprider_project.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'scrapy_sprider_project (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
   'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.128 Safari/537.36',
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  # 'Host': 'www.anquanke.com'
  # 'Host': 'nti.nsfocus.com'
}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'scrapy_sprider_project.middlewares.ScrapySpriderProjectSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html

DOWNLOADER_MIDDLEWARES = {
    # todo 需要代理替换
   # 'scrapy_sprider_project.middlewares.ProxyMiddleware': 543,
   'scrapy_sprider_project.middlewares.BasicProxyMiddleware': 543,
    # 'aroay_cloudscraper.downloadermiddlewares.CloudScraperMiddleware': 500,
    # 'scrapy_sprider_project.ScrapySpriderProjectDownloaderMiddleware':550,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 400,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 300
}
# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    'scrapy_redis.pipelines.RedisPipeline': 100,
    # 'scrapy_sprider_project.pipelines.AncientPoetryPipeline2': 200,
    'scrapy_sprider_project.pipelines.JsonfileProjectPipeline': 300,
    'scrapy_sprider_project.pipelines.ImgsPipLine': 400,
    # 'scrapy_sprider_project.pipelines.MinioPipLine': 450,
    'scrapy_sprider_project.pipelines.MysqlPipeline': 500
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'


# Retry settings
RETRY_ENABLED = True
RETRY_TIMES = 5  # 想重试几次就写几
# 下面这行可要可不要
RETRY_HTTP_CODES = [500, 502, 503, 504, 408, 466]
# todo 图片文件保存路径  后面文件直接保存到minio路径
IMAGES_STORE = 'E:\\scrapy_content\\scrapy_sprider_project\\scrapy_sprider_project\\public_report'
# IMAGES_STORE = 'E:\\pic'
# 90天的图片失效期限
IMAGES_EXPIRES = 90

# todo 指定mysql地址
MYSQL_HOST = "192.168.200.154"
MYSQL_PORT = 4000
MYSQL_DBNAME ="data_operation"
MYSQL_USER = "data_op_admin"
MYSQL_PASSWORD = "fiKEI!0cke&"

# todo 指定minio相关
MINIO_HOST = "10.251.36.86:9000/"
MINIO_ACCESS_KEY = 'admin'
MINIO_SECRET_KEY = 'admin123456'
MINIO_BUCKET = 'images'
MINIO_PATH = 'public_report/'

# todo 指定Redis的主机名和端口
REDIS_HOST = 'localhost'
REDIS_PORT = 6379

# todo 本地路径地址
BASIC_IMG_PATH = ""

# 允许url重定向
MEDIA_ALLOW_REDIRECTS = True

# src替换的地址
SRC_REPLACE_PATH = "/index/PublicReport/getImage?image_path=public_report"

COMMANDS_MODULE = 'scrapy_sprider_project.commands'   # 自己的爬虫名称

# 设置爬取深度
DEPTH_LIMIT = 4

# 调度器启用Redis存储Requests队列
SCHEDULER = "scrapy_redis.scheduler.Scheduler"

# 确保所有的爬虫实例使用Redis进行重复过滤
DUPEFILTER_CLASS = "scrapy_redis.dupefilter.RFPDupeFilter"

# 将Requests队列持久化到Redis，可支持暂停或重启爬虫
SCHEDULER_PERSIST = True

# Requests的调度策略，默认优先级队列
SCHEDULER_QUEUE_CLASS = 'scrapy_redis.queue.PriorityQueue'


# # 默认日志级别
# AROAY_CLOUDSCRAPER_LOGGING_LEVEL = logging.DEBUG()
# LOG_LEVEL = "WARNING"

# # 默认超时
# AROAY_CLOUDSCRAPER_DOWNLOAD_TIMEOUT = 30
#
# # 默认延迟
# AROAY_CLOUDSCRAPER_DELAY = 1
#
# #必须设置，否则报错
# COMPRESSION_ENABLED = False
#
# RETRY_ENABLED: True
# RETRY_TIMES: 3
