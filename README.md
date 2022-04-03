# SCF SCrapy Demo

在云函数上运行 SCrapy 应用示例，对于存量的 Scripy 应用，只需要把该示例中的 `index.py` 添加到代码库即可。和传统单机模式相比：

- 几乎没有运维成本，只需要关注于采集逻辑
- 利用函数的弹性伸缩的特性，支撑海量的数据采集请求
- 性价比更高，按量付费避免资源闲置，提高利用率节约服务器成本

## 本地依赖安装

***⚠️注意：安装依赖过程中设计到二进制文件的构建，MacOS构建的结果无法直接在SCF运行，建议在 Linux / CentOS 执行依赖安装命令：***

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

## 本地压测

```bash
URL="https://service-xxxx-1253970226.gz.apigw.tencentcs.com/release/schedule.json"
echo -n "project=default&spider=toscrape-css" > test.txt | \ 
    cat test.txt | \
    ab -p /dev/stdin -T 'application/x-www-form-urlencoded' \
    -n 100 -c2 $URL
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

### 云端依赖安装

SCF 的在线版本IDE `Cloud Studio` 对于Python 3.7的支持即将发布，可以通过云端环境直接安装依赖，避免环境差异带来的兼容性问题：

1. 打包且不包含第三方依赖：

    ```bash
    zip -r scrapy_demo_1.0.zip . -x "*.git*" -x "*.__MACOSX*" -x "vendor"
    ```
2. 上传 Zip 文件进行函数部署
3. 打开 云端IDE的 Terminal，执行以下命令：

    ```bash
    cd src
    pip3 install -r requirements.txt -t vendor
    ```
4. 重新部署函数

### 异步执行

如果执行时间超过默认允许的超时时间限制，需要开启异步执行模式，可以支持最大 24 小时的执行时间，参考文档：https://cloud.tencent.com/document/product/583/51519

创建函数：

![Run in Async Mode](https://user-images.githubusercontent.com/251222/160980864-05f281ed-0cd3-40ac-a091-1ac46f6149b2.png)

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
