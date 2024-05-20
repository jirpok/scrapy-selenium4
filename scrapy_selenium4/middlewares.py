from typing import Any, Dict, List, Self

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
        browser_ff_prefs: Dict[str, Any] | None = None,
        browser_executable_path: str | None = None,
        command_executor: str | None = None,
    ) -> None:
        """
        Parameters
        ----------
        driver_name : str
            Selenium `WebDriver` to use (`firefox`, `chrome`, `safari`,
            `edge`). Mapped to `SELENIUM_DRIVER_NAME`.

        driver_arguments : List[str] | None, optional
            A list of arguments for `WebDriver` initialization. Mapped
            to `SELENIUM_DRIVER_ARGUMENTS`. By default `None`.

        driver_executable_path : str | None, optional
            Path to driver executable binary. Mapped to
            `SELENIUM_DRIVER_EXECUTABLE_PATH`. By default `None`.

        browser_ff_prefs : Dict[str, Any] | None, optional
            Firefox preferences. Mapped to `SELENIUM_BROWSER_FF_PREFS`.
            By default `None`.

        browser_executable_path : str | None, optional
            Path to browser executable binary. Mapped to
            `SELENIUM_BROWSER_EXECUTABLE_PATH`. By default `None`.

        command_executor : str | None, optional
            Selenium remote server endpoint. Mapped to
            `SELENIUM_COMMAND_EXECUTOR`. By default `None`.
        """

        # SELENIUM_DRIVER_NAME
        # import selected WebDriver
        match driver_name:
            case "firefox":
                from selenium.webdriver import Firefox as WebDriver
                from selenium.webdriver import FirefoxOptions as Options
                from selenium.webdriver import FirefoxService as Service
            case "chrome":
                from selenium.webdriver import Chrome as WebDriver
                from selenium.webdriver import ChromeOptions as Options
                from selenium.webdriver import ChromeService as Service
            case "safari":
                from selenium.webdriver import Safari as WebDriver
                from selenium.webdriver import SafariOptions as Options
                from selenium.webdriver import SafariService as Service
            case "edge":
                from selenium.webdriver import Edge as WebDriver
                from selenium.webdriver import EdgeOptions as Options
                from selenium.webdriver import EdgeService as Service

        options = Options()

        # SELENIUM_DRIVER_ARGUMENTS
        if driver_arguments:
            for arg in driver_arguments:
                options.add_argument(arg)

        # SELENIUM_BROWSER_FF_PREFS
        if browser_ff_prefs:
            for pref, value in browser_ff_prefs.items():
                options.set_preference(pref, value)

        # SELENIUM_BROWSER_EXECUTABLE_PATH
        if browser_executable_path:
            options.binary_location = browser_executable_path

        # SELENIUM_COMMAND_EXECUTOR
        # use remote driver
        if command_executor:
            from selenium.webdriver import Remote
            self.driver = Remote(command_executor=command_executor,
                                 options=options)
        # use local driver
        else:
            service = None
            # SELENIUM_DRIVER_EXECUTABLE_PATH
            if driver_executable_path:
                # OPTIMIZE: import Service here?
                service = Service(executable_path=driver_executable_path)
            self.driver = WebDriver(options, service)

    @classmethod
    def from_crawler(cls, crawler) -> Self:
        driver_name = crawler.settings.get("SELENIUM_DRIVER_NAME")
        driver_arguments = crawler.settings.get("SELENIUM_DRIVER_ARGUMENTS")
        driver_executable_path = crawler.settings.get(
            "SELENIUM_DRIVER_EXECUTABLE_PATH")
        browser_ff_prefs = crawler.settings.get("SELENIUM_BROWSER_FF_PREFS")
        browser_executable_path = crawler.settings.get(
            "SELENIUM_BROWSER_EXECUTABLE_PATH")
        command_executor = crawler.settings.get("SELENIUM_COMMAND_EXECUTOR")

        if driver_name is None:
            raise NotConfigured("SELENIUM_DRIVER_NAME must be set.")

        if driver_executable_path and command_executor:
            raise NotConfigured(
                "Either SELENIUM_DRIVER_EXECUTABLE_PATH "
                "or SELENIUM_COMMAND_EXECUTOR must be set, but not both.")

        if browser_ff_prefs and driver_name != "firefox":
            raise NotConfigured("SELENIUM_BROWSER_FF_PREFS is Firefox-only.")

        middleware = cls(
            driver_name=driver_name,
            driver_arguments=driver_arguments,
            driver_executable_path=driver_executable_path,
            browser_ff_prefs=browser_ff_prefs,
            browser_executable_path=browser_executable_path,
            command_executor=command_executor,
        )

        crawler.signals.connect(middleware.spider_closed,
                                signals.spider_closed)
        return middleware

    def process_request(self, request, spider) -> HtmlResponse | None:

        if not isinstance(request, SeleniumRequest):
            return None

        self.driver.get(request.url)

        for cookie_name, cookie_value in request.cookies.items():
            self.driver.add_cookie({
                "name": cookie_name,
                "value": cookie_value
            })

        if request.wait_until:
            WebDriverWait(self.driver,
                          request.wait_time).until(request.wait_until)

        if request.screenshot:
            request.meta["screenshot"] = self.driver.get_screenshot_as_png()

        if request.script:
            self.driver.execute_script(request.script)

        body = str.encode(self.driver.page_source)

        # expose WebDriver in request meta
        request.meta.update({"driver": self.driver})

        return HtmlResponse(self.driver.current_url,
                            body=body,
                            encoding="utf-8",
                            request=request)

    def spider_closed(self) -> None:
        """Shutdown WebDriver."""
        self.driver.quit()
