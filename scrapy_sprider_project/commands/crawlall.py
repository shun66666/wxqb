import subprocess


def crawl_work():
    # subprocess.Popen('scrapy crawl lmkj_spider', shell=True).wait()
    # subprocess.Popen('scrapy crawl anheng_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl anquanke_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl hkjs_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl hackernews_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl bleepingcomputer_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl infosecurity_magazine_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl cybersecuritynews_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl krebsonsecurity_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl itsecurityguru_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl securityaffairs_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl securitylab_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl cyberscoop_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl govinfosecurity_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl therecord_spider', shell=True).wait()
    subprocess.Popen('scrapy crawl feeds_spider', shell=True).wait()


if __name__ == '__main__':
    crawl_work()


