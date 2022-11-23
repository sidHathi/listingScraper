from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions
from bs4 import BeautifulSoup
from ParsingModel import TagModel
import re
from QueryParams import LeaseTerm

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

def findIntegerMonths(domContent: str) -> list[int] | None:
    regex = re.compile(r'\d+[\s, \A\Z](month|months)')
    matchingSubstrings: list[str] = regex.findall(domContent)
    monthVals: list[int] = []
    added: set = set()
    if len(matchingSubstrings) < 1:
        return None
    for match in matchingSubstrings:
        split = match.split(' ')
        assert(len(split) > 0)
        val = int(split[0])
        if val not in added:
            monthVals.append(val)
            added.add(val)
    return monthVals

def findIntegerListMonths(domContent: str) -> list[int] | None:
    regex = re.compile(r'[\s\d]+(,[\s\d]+)*\s*(or|and)*\s*\d*\s(month|months)')
    matchingSubstrings: list[str] = regex.findall(domContent)
    monthVals: list[int] = []
    added: set = set()
    if len(matchingSubstrings) < 1:
        return None
    for match in matchingSubstrings:
        split = match.split(',')
        assert(len(split) > 0)
        for splitStr in split:
            valStr = re.sub(r'[^0-9]', '', splitStr)
            if len(valStr) > 1:
                val = int(valStr)
                if val not in added:
                    monthVals.append(val)
                    added.add(val)
    return monthVals

def matchKeyword(domContent: str, keyword: str) -> bool:
    if keyword in domContent:
        return True
    return False

def matchLeaseTermByKeyword(domContent: str, keyDict: dict[str, LeaseTerm]) -> list[LeaseTerm]:
    matches: list[LeaseTerm] = []
    for keyword in keyDict:
        if matchKeyword(domContent, keyword):
            matches.append(keyDict[keyword])
    return matches    