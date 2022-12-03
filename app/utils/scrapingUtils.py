from selenium import webdriver
from bs4 import BeautifulSoup
from typing import Any, AnyStr
import re


from ..models.TagModel import TagModel
from ..enums import LeaseTerm

async def htmlPull(url: str, browser: webdriver.Chrome, timeout: int) -> str:
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
    regex = re.compile(r'(\d+[-,\s]*(months|month))', re.IGNORECASE)
    matches = regex.findall(domContent)
    if matches is  None:
        return None
    def getMatchFromGroup(group):
        return group[0]
    matchingSubstrings: list[str] = list(map(getMatchFromGroup, matches))
    monthVals: list[int] = []
    added: set = set()
    if len(matchingSubstrings) < 1:
        return None
    for match in matchingSubstrings:
        split = re.split(r'[,\s]', match)
        assert(len(split) > 0)
        val = int(split[0])
        if val not in added:
            monthVals.append(val)
            added.add(val)
    return monthVals

def findIntegerListMonths(domContent: str) -> list[int] | None:
    regex = re.compile(r'([\d\s]+(,[\s\d]+)*\s*(or|and)*\s*\d*[-\s](months|month))', re.IGNORECASE)
    matches = regex.findall(domContent)
    if matches is  None:
        return None
    def getMatchFromGroup(group):
        return group[0]
    matchingSubstrings: list[str] = list(map(getMatchFromGroup, matches))
    monthVals: list[int] = []
    added: set = set()
    if len(matchingSubstrings) < 1:
        return None
    for match in matchingSubstrings:
        split = re.split(r'[,\s]', match)
        assert(len(split) > 0)
        for splitStr in split:
            valStr = re.sub(r'[^\d]', '', splitStr)
            if len(valStr) >= 1:
                val = int(valStr)
                if val not in added:
                    monthVals.append(val)
                    added.add(val)
    return monthVals

def matchRegex(matchString: str, searchString: str, flags: list[re.RegexFlag]) -> str | None:
    regex = re.compile(matchString, *flags)
    search = regex.search(searchString)
    if search is None:
        return None
    addr: str = search.group()
    return addr

def findCompleteAddress(domContent: str) -> str | None:
    return matchRegex(r'(\d+\s(\w+\s){1,4}(Ave|St|Rd|Dr|Cir|BLVD|CT|EXPY|FWY|LN|PKY|RD|SQ|TPKE)[\s,]{0,2}(NE|NW|SE|SW|E|W|N|S){0,1}[\s,]{0,2}([A-Za-z]+[\s,]{1,2}){0,3}[A-Z]{2,3}(\s\d+){0,1})', domContent, [re.IGNORECASE])

def findCityStatePair(domContent: str) -> str | None:
    return matchRegex(r'(([A-Z][a-z]+[\s,.]{0,2}){1,4}[A-Z]{2,3})', domContent, [])

def findPrice(domContent: str) -> str | None:
    priceStr = matchRegex(r'(\$[\d.,]+\s{0,1}\/)', domContent, [])
    if priceStr is None:
        return None
    
    numeric = re.sub(r'[^0-9]', '', priceStr)
    return numeric

def matchKeyword(domContent: str, keyword: str) -> bool:
    if keyword.upper() in map(str.upper, domContent):
        return True
    return False

def matchLeaseTermByKeyword(domContent: str, keyDict: dict[str, LeaseTerm]) -> list[LeaseTerm]:
    matches: list[LeaseTerm] = []
    for keyword in keyDict:
        if matchKeyword(domContent, keyword):
            matches.append(keyDict[keyword])
    return matches