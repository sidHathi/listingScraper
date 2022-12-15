from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from undetected_chromedriver import Chrome as ucChrome

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from typing import Any
from time import sleep
import json

from .selenium_python import smartproxy
from .models.TagModel import TagModel


proxyUrl: str = 'http://gate.smartproxy.com:7000'
maxRetires: int = 3
requestTimeout: int = 10
requiresProxy: bool | None = None;

class RequestHub:
    def __init__(self) -> None:
        print('rqh initializing')
        software_names: list[str] = [SoftwareName.CHROME.value]
        operating_systems: list[str] = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MACOS.value]

        self.user_agent_rotator: UserAgent = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    
        self.prox = Proxy()
        self.prox.proxy_type = ProxyType.MANUAL
        self.prox.auto_detect = False
        self.prox.http_proxy = proxyUrl
        self.prox.ssl_proxy = proxyUrl
        # self.proxyCapabilities = webdriver.DesiredCapabilities.CHROME
        # prox.add_to_capabilities(self.proxyCapabilities)

    def tryRequest(self, url: str, elemOnSuccess: TagModel, proxy: bool) -> str | None:
        userAgent: str = self.user_agent_rotator.get_random_user_agent()
        opts = Options()
        opts.add_argument(f'user-agent={userAgent}')
        opts.add_argument('--no-sandbox')
        opts.add_argument('--window-size=1920x1080')
        opts.add_argument('--single-process')
        opts.add_argument('--disable-dev-shm-usage')
        opts.add_argument('--ignore-certificate-errors')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument('--disable-blink-features=AutomationControlled')
        opts.add_argument("--disable-infobars")

        if proxy:
            opts.add_argument(f'--proxy-server={proxyUrl}')
            browser = ucChrome(options=opts, desired_capabilities=smartproxy())
        else:
            browser = ucChrome(options=opts)

        for _ in range(maxRetires):
            browser.get(url)
            try:
                print(elemOnSuccess.getCssSelector())
                WebDriverWait(browser, requestTimeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        elemOnSuccess.getCssSelector()))
                )
            except TimeoutException:
                print(f'timeout for {url}')
                return None
            except WebDriverException as e:
                print(e)
                sleep(6)
                continue
            
            print('successful scrape')
            # browser.maximize_window()
            html: str = browser.page_source
            browser.close()
            return html

    def executeRequest(self, url: str, elemOnSuccess: TagModel) -> str | None:
        '''
        TO-DO: Implement the following functionality 
        1. Randomly choose a browser from the list of simpleBrowsers
            - make the request
            - If the request times out -> exit
            - If the request is unsuccessful -> try again for # of retries
            (skip this step if proxyUse is true)
        2. Randomly choose a browser from the list of proxyBrowsers
            - make the request
            - If the request times out -> exit
            - If the request is unsuccessful -> try again for # of retries
            (skip this step if proxyUse is false)
        3. Return the first successful result of None
        '''
        # Step one
        if requiresProxy is None or not requiresProxy:
            res: str | None = self.tryRequest(url, elemOnSuccess, False)
            if res is not None:
                print("valid result without proxy")
                return res
        if requiresProxy is None or requiresProxy:
            res: str | None = self.tryRequest(url, elemOnSuccess, True)
            if res is not None:
                print("valid result with proxy")
                return res


