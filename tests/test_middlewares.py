from unittest.mock import patch
from scrapy import Request
from scrapy.crawler import Crawler
from scrapy_selenium4.http import SeleniumRequest
from scrapy_selenium4.middlewares import SeleniumMiddleware
from .test_cases import BaseScrapySeleniumTestCase


class SeleniumMiddlewareTestCase(BaseScrapySeleniumTestCase):
    """Test case for SeleniumMiddleware."""

    @classmethod
    def setUpClass(cls):
        """Initialize middleware."""
        super().setUpClass()
        crawler = Crawler(spidercls=cls.spider_klass, settings=cls.settings)
        cls.selenium_middleware = SeleniumMiddleware.from_crawler(crawler)

    @classmethod
    def tearDownClass(cls):
        """Close Selenium driver."""
        super().tearDownClass()
        cls.selenium_middleware.driver.quit()

    def test_from_crawler_initializes_driver(self):
        """The `from_crawler` method should initialize the Selenium
        driver."""
        crawler = Crawler(spidercls=self.spider_klass, settings=self.settings)
        selenium_middleware = SeleniumMiddleware.from_crawler(crawler)

        # the driver must be initialized
        self.assertIsNotNone(selenium_middleware.driver)

        # use the driver
        selenium_middleware.driver.get("http://www.python.org")
        self.assertIn("Python", selenium_middleware.driver.title)

        selenium_middleware.driver.close()

    def test_spider_closed_closes_driver(self):
        """The `spider_closed` method should close the Selenium driver."""
        crawler = Crawler(spidercls=self.spider_klass, settings=self.settings)
        selenium_middleware = SeleniumMiddleware.from_crawler(crawler)

        with patch.object(selenium_middleware.driver, "quit") as mocked_quit:
            selenium_middleware.spider_closed()

        mocked_quit.assert_called_once()

    def test_process_request_returns_none_if_not_selenium_request(self):
        """The `process_request` method should return `None` if not
        `SeleniumRequest`."""

        scrapy_request = Request(url="http://not-an-url")

        self.assertIsNone(
            self.selenium_middleware.process_request(
                request=scrapy_request, spider=None
            )
        )

    def test_process_request_returns_response_if_selenium_request(self):
        """The `process_request` method should return response if
        `SeleniumRequest`."""

        selenium_request = SeleniumRequest(url="http://www.python.org")

        html_response = self.selenium_middleware.process_request(
            request=selenium_request, spider=None
        )

        # use `meta` to access the driver on the response
        self.assertEqual(html_response.meta["driver"], self.selenium_middleware.driver)

        self.assertEqual(
            html_response.selector.xpath("//title/text()").extract_first(),
            "Welcome to Python.org",
        )

    def test_process_request_returns_screenshot_if_true(self):
        """Test `screenshot=True`."""

        selenium_request = SeleniumRequest(url="http://www.python.org", screenshot=True)

        html_response = self.selenium_middleware.process_request(
            request=selenium_request, spider=None
        )

        self.assertIsNotNone(html_response.meta["screenshot"])

    def test_process_request_executes_script_if_set(self):
        """Test `script=<str>`."""

        selenium_request = SeleniumRequest(
            url="http://www.python.org", script='document.title = "scrapy_selenium";'
        )

        html_response = self.selenium_middleware.process_request(
            request=selenium_request, spider=None
        )

        self.assertEqual(
            html_response.selector.xpath("//title/text()").extract_first(),
            "scrapy_selenium",
        )
