from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from ParsingModel import TagModel

async def htmlPull(url: str, timeout: int) -> str:
    opts = ChromeOptions()
    browser = webdriver.Chrome('chromedriver', options=opts)
    browser.maximize_window()
    browser.get(url)
    browser.implicitly_wait(timeout)
    return browser.page_source

def followTagMap(tagMap: list[TagModel], dom: BeautifulSoup) -> list[BeautifulSoup]:
    currentTagList = []
    for step in tagMap:
        if len(currentTagList) < 1:
            currentTagList = dom.find_all(step.tagType, step.identifiers)
            continue
        nextTagList = []
        for tag in currentTagList:
            nextTagList.extend(tag.find_all(step.tagType, step.identifiers))
        currentTagList = nextTagList
    return currentTagList