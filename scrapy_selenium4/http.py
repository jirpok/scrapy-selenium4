from scrapy.http import Request

from selenium.webdriver.support import expected_conditions


class SeleniumRequest(Request):
    """Subclass of `scrapy.http.Request` providing additional arguments."""

    def __init__(
        self,
        wait_time: int | None = None,
        wait_until=None,
        screenshot: bool = False,
        script: str | None = None,
        *args,
        **kwargs
    ):
        """Initialize new Selenium request.

        Parameters
        ----------
        wait_time : int | None, optional
            The number of seconds to wait, by default `None`.
        wait_until : _type_, optional
            One of the `selenium.webdriver.support.expected_conditions`.
            The response will not be returned until the given condition
            is fulfilled. By default `None`.
        screenshot : bool, optional
            If `True`, takes a screenshot of the page and returns the
            data in the response `meta` attribute. By default `False`.
        script : str | None, optional
            JavaScript code to execute. By default `None`.
        """

        self.wait_time = wait_time
        self.wait_until = wait_until
        self.screenshot = screenshot
        self.script = script

        super().__init__(*args, **kwargs)
