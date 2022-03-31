import sys
import os
import json

parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)

from scrapy.utils.project import get_project_settings
from scrapy.crawler import CrawlerProcess
from scrapy.spiderloader import SpiderLoader

def main_handler(event, context):
    if event.get('body'):
        spider_event = json.loads(event['body'])
        print("trigger spider from apgw with event {0}".format(spider_event))
        crawl(**spider_event)
    else:
        print("trigger spider with event {0}".format(event))
        crawl(**event)


def crawl(settings={}, spider_name="toscrape-css", spider_kwargs={}):
    project_settings = get_project_settings()
    spider_loader = SpiderLoader(project_settings)

    spider_cls = spider_loader.load(spider_name)

    #SCF can only write to the /tmp folder.
    settings['HTTPCACHE_DIR'] = "/tmp"
    settings['FEED_URI'] = ""
    settings['FEED_FORMAT'] = "json"

    process = CrawlerProcess({**project_settings, **settings})

    process.crawl(spider_cls, **spider_kwargs)
    process.start()


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