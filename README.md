# Selenium 4 middleware for Scrapy

Fork of [scrapy-selenium](https://github.com/clemfromspace/scrapy-selenium)
working with the recent versions of Selenium 4.

All settings except `SELENIUM_DRIVER_NAME` are now optional. The middleware
_should_ still work with existing Scrapy projects integrating the upstream
package.

# Requirements

Tested with `python3.12`. You will need a [Selenium 4 compatible browser](https://www.selenium.dev/documentation/webdriver/browsers/).

# Installation

With [Poetry](https://python-poetry.org/)

```shell
poetry add git+https://github.com/jirpok/scrapy-selenium4.git
```

# Configuration

(Edge and Safari are also supported.)

## Firefox

```python
SELENIUM_DRIVER_NAME = "firefox"
SELENIUM_DRIVER_ARGUMENTS = ["-headless"]
SELENIUM_BROWSER_FF_PREFS = {
    "javascript.enabled": False,    # disable JavaScript
    "permissions.default.image": 2  # block all images from loading
}
```

[Firefox/CommandLineOptions](https://wiki.mozilla.org/Firefox/CommandLineOptions)

### Proxy settings

#### SOCKS5

```python
SELENIUM_BROWSER_FF_PREFS = {
    "network.proxy.type": 1,
    "network.proxy.socks_remote_dns": True,
    "network.proxy.socks": "<HOST>",
    "network.proxy.socks_port": <PORT>
}
```

#### HTTP(S)

```python
"SELENIUM_BROWSER_FF_PREFS": {
    "network.proxy.type": 1,
    "network.proxy.http": "<HOST>",
    "network.proxy.http_port": <PORT>,
    "network.proxy.ssl": "<HOST>",
    "network.proxy.ssl_port": <PORT>
}
```

## Chrome

```python
SELENIUM_DRIVER_NAME = "chrome"
SELENIUM_DRIVER_ARGUMENTS=["--headless=new"]
```

## Optional settings

### Specify path to the browser executable

```python
SELENIUM_BROWSER_EXECUTABLE_PATH = "path/to/browser/executable"
```

### Specify path to the local driver

Selenium requires a driver ([GeckoDriver](https://github.com/mozilla/geckodriver/releases),
[ChromeDriver](https://developer.chrome.com/docs/chromedriver), …) to interface
with the chosen browser. Recent versions of Selenium 4 ship with the [Selenium Manager](https://www.selenium.dev/documentation/selenium_manager/),
automatically handling these dependencies.

```python
SELENIUM_DRIVER_EXECUTABLE_PATH = "path/to/driver/executable"
```

### Specify remote driver

```python
SELENIUM_COMMAND_EXECUTOR = "http://localhost:4444/wd/hub"
```

(Do not set `SELENIUM_DRIVER_EXECUTABLE_PATH` along with
`SELENIUM_COMMAND_EXECUTOR`.)

## Include in `DOWNLOADER_MIDDLEWARE`

```python
DOWNLOADER_MIDDLEWARES = {
    "scrapy_selenium4.SeleniumMiddleware": 800
}
```

# Usage

Use the `scrapy_selenium4.SeleniumRequest` instead of the scrapy built-in
`Request`:

```python
from scrapy_selenium4 import SeleniumRequest

yield SeleniumRequest(url=url, callback=self.parse)
```

Such request will have an additional `meta` key `driver` containing the Selenium
driver with the request processed.

```python
def parse(self, response):
    print(response.request.meta["driver"].title)
```

## Additional arguments

### `wait_time`, `wait_until`

[Explicit wait](https://www.selenium.dev/documentation/webdriver/waits/#explicit-waits)
before returning the response to the spider.

```python
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

yield SeleniumRequest(
    url=url,
    callback=self.parse,
    wait_time=10,
    wait_until=EC.element_to_be_clickable((By.ID, "some_id"))
)
```

### `screenshot`

Take a screenshot of the page and add the binary data of the captured .png to
the response `meta`.

```python
yield SeleniumRequest(
    url=url,
    callback=self.parse,
    screenshot=True
)

def parse(self, response):
    with open("image.png", "wb") as image_file:
        image_file.write(response.meta["screenshot"])
```

### `script`

Execute custom JavaScript code.

```python
yield SeleniumRequest(
    url=url,
    callback=self.parse,
    script="window.scrollTo(0, document.body.scrollHeight);",
)
```
