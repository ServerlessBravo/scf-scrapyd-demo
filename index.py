import sys
import os
import json

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

from multiprocessing import Process
from twisted.internet import reactor
from scrapy.crawler import CrawlerRunner
from scrapy.spiderloader import SpiderLoader
from scrapy.utils.log import configure_logging
from scrapy.utils.project import get_project_settings


def main_handler(event, context):
    spider_event = event
    if event.get('body'):
        spider_event = json.loads(event['body'])

    print("trigger spider with event {0}".format(spider_event))
    try:
        crawl(**spider_event)
        return "OK"
    except Exception as e:
        print(e)
        raise e

def run_spider(spider_name, project_settings, spider_kwargs):
    runner = CrawlerRunner(project_settings)
    deferred = runner.crawl(spider_name)

    spider_loader = SpiderLoader(project_settings)
    spider_cls = spider_loader.load(spider_name)
    runner.crawl(spider_cls, **spider_kwargs)

    deferred.addBoth(lambda _: reactor.stop())
    reactor.run()


def crawl(settings={}, spider_name="toscrape-css", spider_kwargs={}):
    project_settings = get_project_settings()
    configure_logging(project_settings)

    # SCF can only write to the /tmp folder.
    settings['HTTPCACHE_DIR'] = "/tmp"
    settings['FEED_URI'] = ""
    settings['FEED_FORMAT'] = "json"

    crawler_process = Process(target=run_spider, args=(spider_name, project_settings, spider_kwargs))
    crawler_process.start()
    crawler_process.join()


if __name__ == "__main__":
    event = {
        "spider_name": "toscrape-css",
        "spider_kwargs": {
            "key1": "value1",
            "key2": "value2"
        }
    }
    main_handler(event, {})

    # sample apigw event
    # apigw_event = {
    #     "body": "{\n    \"spider_name\": \"toscrape-css\",\n    \"spider_kwargs\": {\n        \"key1\": \"value1\",\n        \"key2\": \"value2\"\n    }\n}",
    #     "headerParameters": {},
    #     "headers": {
    #         "accept": "*/*",
    #         "accept-encoding": "gzip, deflate, br",
    #     },
    #     "httpMethod": "POST",
    #     "isBase64Encoded": "false",
    #     "path": "/python_simple_demo",
    #     "pathParameters": {},
    #     "queryString": {},
    #     "queryStringParameters": {}
    # }
    # main_handler(apigw_event, {})
