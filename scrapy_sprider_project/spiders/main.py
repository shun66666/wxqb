import os
import sys
from scrapy import cmdline


if __name__ == '__main__':
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    # 'lmkj_spider', 'anquanke_spider', 'anheng_spider', 'hkjs_spider', hackernews_spider, 'bleepingcomputer_spider', "infosecurity_magazine_spider"
    cmdline.execute('scrapy crawl feeds_spider'.split())
    # cmdline.execute('scrapy crawl hkjs_spider'.split())
    print("end")