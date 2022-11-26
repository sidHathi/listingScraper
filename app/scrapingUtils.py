from selenium import webdriver
from bs4 import BeautifulSoup
from .models.TagModel import TagModel
import re
from .enums import LeaseTerm

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