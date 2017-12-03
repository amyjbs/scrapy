# -*- coding: utf-8 -*-
__author__ = 'bobby'

from scrapy.http import Request
from urllib import parse
import datetime
from scrapy_redis.spiders import RedisSpider
from ScrapyRedisTest.items import ScrapyredistestItem
class JobboleSpider(RedisSpider):
    name = 'jobbole'
    allowed_domains = ["blog.jobbole.com"]
    redis_key = 'jobbole:start_urls'

    # 收集伯乐在线所有404的url以及404页面数
    handle_httpstatus_list = [404]


    def parse(self, response):
        """
        1. 获取文章列表页中的文章url并交给scrapy下载后并进行解析
        2. 获取下一页的url并交给scrapy进行下载， 下载完成后交给parse
        """
        # 解析列表页中的所有文章url并交给scrapy下载后并进行解析
        if response.status == 404:
            self.fail_urls.append(response.url)
            self.crawler.stats.inc_value("failed_url")

        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")
            post_url = post_node.css("::attr(href)").extract_first("")
            yield Request(url=parse.urljoin(response.url, post_url), meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页并交给scrapy进行下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        item = ScrapyredistestItem()

        title = response.css(".entry-header h1::text").extract()[0]
        create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·","").strip()
        fav_nums = response.css(".bookmark-btn::text").extract()[0]
        item["title"] = title
        item["url"] = response.url
        try:
            create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        except Exception as e:
            create_date = datetime.datetime.now().date()
        item["create_date"] = create_date
        item["fav_nums"] = fav_nums

        yield item