from selenium import webdriver
from selenium.common.exceptions import TimeoutException, WebDriverException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.proxy import Proxy, ProxyType
from undetected_chromedriver import Chrome as ucChrome
from webdriver_manager.chrome import ChromeDriverManager

from random_user_agent.user_agent import UserAgent
from random_user_agent.params import SoftwareName, OperatingSystem

from typing import Any
from time import sleep
from dotenv import dotenv_values

from .selenium_python import smartproxy
from .models.TagModel import TagModel


proxyUrl: str = 'http://geo.iproyal.com:12321'
maxRetires: int = 3
requestTimeout: int = 10
config = dotenv_values('.env')

class RequestHub:
    def __init__(self) -> None:
        assert config['PROXY_AVAILABLE'] is not None
        print('rqh initializing')
        software_names: list[str] = [SoftwareName.CHROME.value]
        operating_systems: list[str] = [OperatingSystem.WINDOWS.value, OperatingSystem.LINUX.value, OperatingSystem.MACOS.value]

        self.user_agent_rotator: UserAgent = UserAgent(software_names=software_names, operating_systems=operating_systems, limit=100)
    
        self.prox = Proxy()
        self.prox.proxy_type = ProxyType.MANUAL
        self.prox.auto_detect = False
        self.prox.http_proxy = proxyUrl
        self.prox.ssl_proxy = proxyUrl

        match config['PROXY_AVAILABLE']:
            case 'yes':
                self.proxyAvailable = True
            case 'no':
                self.proxyAvailable = False

    def tryRequest(self, url: str, elemOnSuccess: TagModel, proxy: bool = False, headless: bool = False) -> str | None:
        for _ in range(maxRetires):
            userAgent: str = self.user_agent_rotator.get_random_user_agent()

            try:
                opts = Options()
                opts.add_argument(f'user-agent={userAgent}')
                opts.add_argument('accept=text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng')
                opts.add_argument('accept-encoding=gzip,deflate,br')
                opts.add_argument('accept-language=en-US,en;q=0.8')
                opts.add_argument('dnt=1')
                opts.add_argument('upgrade-insecure-requests=1')
                opts.add_argument('--single-process')
                opts.add_argument('--disable-dev-shm-usage')
                opts.add_argument('--ignore-certificate-errors')
                opts.add_argument('--disable-blink-features=AutomationControlled')
                opts.add_argument("--disable-infobars")
                opts.add_argument("--disable-extensions")
                opts.add_argument('--disable-application-cache')
                opts.add_argument('--disable-gpu')
                opts.add_argument("--no-sandbox")
                opts.add_argument("--disable-setuid-sandbox")
                
                if headless:
                    opts.add_argument('--headless')

                if proxy:
                    opts.add_argument(f'--proxy-server={proxyUrl}')
                    # opts.add_argument(f'Connection=close')
                    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=opts)
                else:
                    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=opts)
                browser.get(url)
                print(elemOnSuccess.getCssSelector())
                WebDriverWait(browser, requestTimeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, 
                        elemOnSuccess.getCssSelector()))
                )
            except TimeoutException:
                print(f'timeout for {url}')
                sleep(6)
                return None
            except WebDriverException as e:
                print(e)
                sleep(6)
                return None
            except Exception as e:
                print(e)
                sleep(6)
                return None

            print('successful scrape')
            # browser.maximize_window()
            html: str = browser.page_source
            browser.close()
            return html
        return None

    def executeRequest(self, url: str, elemOnSuccess: TagModel, proxy: bool, headless: bool = False) -> str | None:
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
        useProxy: bool = self.proxyAvailable and proxy
        res: str | None = self.tryRequest(url, elemOnSuccess, useProxy, headless)
        if res is not None and useProxy:
            print("valid result with proxy")
            return res
        elif res is not None and not useProxy:
            print("valid result without proxy")
            return res



