from typing import Any

from scrapy.http import Request


class SeleniumRequest(Request):
    """Subclass of `scrapy.http.Request` providing additional arguments."""

    def __init__(self,
                 wait_time: int | None = None,
                 wait_until: Any | None = None,
                 screenshot: bool = False,
                 script: str | None = None,
                 *args,
                 **kwargs) -> None:
        """
        Parameters
        ----------
        wait_time : int | None, optional
            The number of seconds to wait. By default `None`.

        wait_until : Any | None, optional
             One of the `selenium.webdriver.support.expected_conditions`.
            The response will not be returned until the given condition
            is fulfilled. By default `None`.

        screenshot : bool, optional
            If `True`, take a screenshot of the page and return the
            data in the response `meta` attribute. By default `False`.

        script : str | None, optional
            JavaScript code to execute. By default `None`.
        """
        self.wait_time = wait_time
        self.wait_until = wait_until
        self.screenshot = screenshot
        self.script = script

        super().__init__(*args, **kwargs)
