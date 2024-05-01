from unittest import TestCase

import scrapy


class BaseScrapySeleniumTestCase(TestCase):
    """Base test case for the `scrapy-selenium4` package."""

    class SimpleSpider(scrapy.Spider):
        name = "simple_spider"
        allowed_domains = ["python.org"]
        start_urls = ["http://python.org"]

        def parse(self, response):
            pass

    @classmethod
    def setUpClass(cls):
        """Create a scrapy process and a spider class to use in the
        tests."""

        cls.settings = {
            "SELENIUM_DRIVER_NAME": "firefox",
            "SELENIUM_DRIVER_ARGUMENTS": ["-headless"],
        }
        cls.spider_klass = cls.SimpleSpider
