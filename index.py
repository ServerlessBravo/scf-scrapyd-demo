import sys
import os

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader

def main_handler(event, context):
    crawl(**event)


def crawl(settings={}, spider_name="toscrape-css", spider_kwargs={}):
    project_settings = get_project_settings()
    spider_loader = SpiderLoader(project_settings)

    spider_cls = spider_loader.load(spider_name)

    feed_uri = ""
    feed_format = "json"

    #SCF can only write to the /tmp folder.
    settings['HTTPCACHE_DIR'] = "/tmp"
    settings['FEED_URI'] = feed_uri
    settings['FEED_FORMAT'] = feed_format

    process = CrawlerProcess({**project_settings, **settings})

    process.crawl(spider_cls, **spider_kwargs)
    process.start()


if __name__ == "__main__":
    event = {
        "spider_name": 'toscrape-css'
    }
    main_handler(event, {})
