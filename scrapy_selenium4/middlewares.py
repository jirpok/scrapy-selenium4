from typing import List
from scrapy import signals
from scrapy.exceptions import NotConfigured
from scrapy.http import HtmlResponse
from selenium.webdriver.support.ui import WebDriverWait
from .http import SeleniumRequest


class SeleniumMiddleware:
    """Selenium 4 Scrapy middleware."""

    def __init__(
        self,
        driver_name: str,
        driver_arguments: List[str] | None = None,
        driver_executable_path: str | None = None,
        browser_executable_path: str | None = None,
        command_executor: str | None = None,
    ) -> None:
        """Initialize Selenium WebDriver.

        Parameters
        ----------
        driver_name : str
            Selenium `WebDriver` to use (`firefox`, `chrome`, `safari`,
            `edge`). Mapped to `SELENIUM_DRIVER_NAME`.
        driver_arguments : List[str] | None, optional
            A list of arguments for `WebDriver` initialization. Mapped
            to `SELENIUM_DRIVER_ARGUMENTS`, by default `None`.
        driver_executable_path : str | None, optional
            Path to driver executable binary. Mapped to
            `SELENIUM_DRIVER_EXECUTABLE_PATH`, by default `None`
        browser_executable_path : str | None, optional
            Path to browser executable binary. Mapped to
            `SELENIUM_BROWSER_EXECUTABLE_PATH`, by default `None`
        command_executor : str | None, optional
            Selenium remote server endpoint. Mapped to
            `SELENIUM_COMMAND_EXECUTOR`, by default `None`.
        """

        # SELENIUM_DRIVER_NAME
        # import selected WebDriver
        match driver_name:
            case "firefox":
                from selenium.webdriver import (
                    Firefox as WebDriver,
                    FirefoxOptions as Options,
                    FirefoxService as Service,
                )
            case "chrome":
                from selenium.webdriver import (
                    Chrome as WebDriver,
                    ChromeOptions as Options,
                    ChromeService as Service,
                )
            case "safari":
                from selenium.webdriver import (
                    Safari as WebDriver,
                    SafariOptions as Options,
                    SafariService as Service,
                )
            case "edge":
                from selenium.webdriver import (
                    Edge as WebDriver,
                    EdgeOptions as Options,
                    EdgeService as Service,
                )

        options = Options()

        # SELENIUM_DRIVER_ARGUMENTS
        for arg in driver_arguments:
            options.add_argument(arg)

        # SELENIUM_BROWSER_EXECUTABLE_PATH
        if browser_executable_path:
            options.binary_location = browser_executable_path

        # SELENIUM_COMMAND_EXECUTOR
        # use remote driver
        if command_executor:
            from selenium.webdriver import Remote

            self.driver = Remote(command_executor=command_executor, options=options)
        # use local driver
        else:
            service = None
            # SELENIUM_DRIVER_EXECUTABLE_PATH
            if driver_executable_path:
                # OPTIMIZE: import Service here?
                service = Service(executable_path=driver_executable_path)
            self.driver = WebDriver(options, service)

    @classmethod
    def from_crawler(cls, crawler):
        """Initialize middleware."""

        driver_name = crawler.settings.get("SELENIUM_DRIVER_NAME")
        driver_arguments = crawler.settings.get("SELENIUM_DRIVER_ARGUMENTS")
        driver_executable_path = crawler.settings.get("SELENIUM_DRIVER_EXECUTABLE_PATH")
        browser_executable_path = crawler.settings.get(
            "SELENIUM_BROWSER_EXECUTABLE_PATH"
        )
        command_executor = crawler.settings.get("SELENIUM_COMMAND_EXECUTOR")

        if driver_name is None:
            raise NotConfigured("SELENIUM_DRIVER_NAME must be set.")

        if driver_executable_path is not None and command_executor is not None:
            raise NotConfigured(
                "Either SELENIUM_DRIVER_EXECUTABLE_PATH "
                "or SELENIUM_COMMAND_EXECUTOR must be set, but not both."
            )

        middleware = cls(
            driver_name=driver_name,
            driver_executable_path=driver_executable_path,
            browser_executable_path=browser_executable_path,
            command_executor=command_executor,
            driver_arguments=driver_arguments,
        )

        crawler.signals.connect(middleware.spider_closed, signals.spider_closed)
        return middleware

    def process_request(self, request, spider):
        """Process request."""

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie({"name": cookie_name, "value": cookie_value})

        if request.wait_until:
            WebDriverWait(self.driver, request.wait_time).until(request.wait_until)

        if request.screenshot:
            request.meta["screenshot"] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # expose the driver via the `meta` attribute
        request.meta.update({"driver": self.driver})

        return HtmlResponse(
            self.driver.current_url, body=body, encoding="utf-8", request=request
        )

    def spider_closed(self):
        """Shutdown the driver when spider is closed."""
        self.driver.quit()
