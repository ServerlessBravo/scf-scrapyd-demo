# SCF SCrapy Demo

在云函数上运行 SCrapy 应用示例，对于存量的 Scripy 应用，只需要把该示例中的 `index.py` 添加到代码库即可。

## 本地依赖安装

通过把所有的依赖导出到 `vendor` 目录，项目结构更加清晰：

```bash
pyenv exec pip3 install -r requirements.txt -t vendor
```

在SCF的入口函数处，把 `vendor` 目录加入的引用的路径中，如示例代码 `index.py` 文件:

```python
parent_dir = os.path.abspath(os.path.dirname(__file__))
vendor_dir = os.path.join(parent_dir, 'vendor')
sys.path.insert(1, vendor_dir)
```

## 本地测试执行

```bash
## 采用pyenv执行
pyenv exec python3 index.py
## 或者
python3 index.py
```
## 打包

```bash
zip -r scrapy_demo_1.0.zip . -x "*.git*" -x "*.__MACOSX*"
```

## 通过 Zip 部署函数

函数配置：

```
函数类型	Event函数
运行环境	Python 3.7
资源类型	CPU
内存	512MB
执行超时时间	300秒
```
其中 `内存配置` 和 `执行超时时间` 根据应用具体的情况进行配置

## 测试

### 通过 Event 直接触发

Sample Event:
```json
{
    "spider_name": "toscrape-css",
    "spider_kwargs": {
        "key1": "value1",
        "key2": "value2"
    } 
}
```

![Test from Console](https://user-images.githubusercontent.com/251222/160966810-9ee929cf-9f3f-4e5c-a4be-013ba43ad30d.png)

### 通过 API 网关触发

- 添加 `APIGW` 触发器，⚠️注意不要开启 **集成响应** 功能
- 获取 `APIGW` 的触发器的地址为：
https://service-xxxxx-1253970226.gz.apigw.tencentcs.com/release/python_simple_demo
- 通过POST方法触发 Scrapy执行，例如
    ```json
    {
    "spider_name": "toscrape-css",
    "spider_kwargs": {
        "key1": "value1",
        "key2": "value2"
        }
    }
    ```

## 其他

### 自定义参数

例如示例中，可以通过 `spider_kwargs` 给对应的应用传递自定义参数，在代码中可以通过以下方式获取：

如 `toscrapy-css.py`：

```python
def __init__(self, **kwargs):
    super(ToScrapeCSSSpider, self).__init__(name=name, **kwargs)

    self.start_urls = [
        'http://quotes.toscrape.com/',
    ]
    ## {"key1": "value1", "key2": "value2" } 
    self.arguments = kwargs
```

### 结果持久化

- 可以通过挂载 `CFS`，把结果持久化到共享文件存储中，修改 `HTTPCACHE_DIR` 环境变量即可，参考链接：https://cloud.tencent.com/document/product/583/46199
- `COS` 原生支持 `S3` 协议，Scrapy的 `Feed_Format` 支持对应的协议，可以通过配置把内容写入到对象存储中 [用法待补充], [查看链接](https://docs.scrapy.org/en/latest/topics/feed-exports.html#topics-feed-storage-s3)

## 参考链接

- QuotesBot: [github repo](https://github.com/scrapinghub/spidyquotes)
- Serverless Scraping with Scrapy, AWS Lambda and Fargate – a guide [Link](https://blog.vikfand.com/posts/scrapy-fargate-sls-guide/)
