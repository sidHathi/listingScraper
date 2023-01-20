from typing import TextIO
import json
from urllib.parse import urlparse

from ..metrics.MetricsController import MetricsController

class RequestLogger:
    def __init__(self, logFile: TextIO | None = None, metricsController: MetricsController | None = None):
        self.logFile = logFile
        self.metricsController: MetricsController | None = metricsController
        self.webDriverFailures: dict[str, dict[str, int]] = {}
        self.timeoutFailures: dict[str, dict[str, int]] = {}
        self.genericFailures: dict[str, dict[str, int]] = {}
        self.proxyFailures: int = 0
        self.nonProxyFailures: int = 0
        self.userAgentBlacklist: dict[str, set[str]] | None = None
        self.blacklistFile: TextIO | None = None

    def addBlacklist(self, blacklist: dict[str, set[str]], writeLoc: TextIO | None):
        print('adding blacklist')
        print(blacklist)
        self.userAgentBlacklist = blacklist
        self.blacklistFile = writeLoc

    def initializeWebdriverDict(self, dict: dict[str, dict[str, int]], userAgent: str, url: str):
        domain: str = urlparse(url).netloc
        if domain not in dict:
            dict[domain] = {}
        if userAgent not in dict[domain]:
            dict[domain][userAgent] = 0

    def addFailureToDict(self, dict: dict[str, dict[str, int]], userAgent: str, url: str, proxyUse: bool):
        domain: str = urlparse(url).netloc
        if self.metricsController is not None:
            failureType: str = 'unknown'
            if dict is self.webDriverFailures:
                failureType = 'webdriver'
            if dict is self.timeoutFailures:
                failureType = 'timeout'
            if dict is self.genericFailures:
                failureType = 'generic'
            self.metricsController.logFailure(domain, proxyUse, failureType)

        if self.userAgentBlacklist is not None:
            if domain not in self.userAgentBlacklist:
                self.userAgentBlacklist[domain] = set()
            self.userAgentBlacklist[domain].add(userAgent)

        if domain not in dict:
            dict[domain] = {}
        if userAgent not in dict[domain]:
            dict[domain][userAgent] = 0

        dict[domain][userAgent] += 1
        if proxyUse:
            self.proxyFailures += 1
        else:
            self.nonProxyFailures += 1

    def logWebdriverFailure(self, userAgent: str, url: str, proxyUse: bool):
        self.addFailureToDict(self.webDriverFailures, userAgent, url, proxyUse)

    def logTimeoutFailure(self, userAgent: str, url: str, proxyUse: bool):
        self.addFailureToDict(self.timeoutFailures, userAgent, url, proxyUse)

    def logGenericFailure(self, userAgent: str, url: str, proxyUse: bool):
        self.addFailureToDict(self.genericFailures, userAgent, url, proxyUse)

    def logSuccess(self, userAgent: str, url: str, proxyUse: bool):
        domain: str = urlparse(url).netloc
        if self.metricsController is not None:
            self.metricsController.logSuccess(domain, proxyUse)
        self.initializeWebdriverDict(self.timeoutFailures, userAgent, url)
        self.initializeWebdriverDict(self.webDriverFailures, userAgent, url)
        self.initializeWebdriverDict(self.genericFailures, userAgent, url)

    def encodeBlackList(self, blacklist: dict[str, set[str]]) -> dict[str, list[str]]:
        out: dict[str, list[str]] = {}
        for key, val in blacklist.items():
            out[key] = list(val)
        return out

    def dumpLogs(self):
        if self.logFile is None:
            print("webdriver failure breakdown:")
            print(self.webDriverFailures)
            print("timeout failure breakdown:")
            print(self.timeoutFailures)
            print("generic failure breakdown:")
            print(self.genericFailures)
            print(f'failures w proxy: {self.proxyFailures}, w/o: {self.nonProxyFailures}')
            return
        self.logFile.write("webdriver failure breakdown:\n")
        self.logFile.write(f'{str(self.webDriverFailures)}\n')
        self.logFile.write("timeout failure breakdown\n")
        self.logFile.write(f'{str(self.timeoutFailures)}\n')
        self.logFile.write("generic failure breakdown:\n")
        self.logFile.write(f'{str(self.genericFailures)}\n')

        print('blacklist ' + str(self.userAgentBlacklist))
        if self.blacklistFile is not None and self.userAgentBlacklist is not None:
            print('writing blacklist file')
            self.blacklistFile.write(json.dumps(self.encodeBlackList(self.userAgentBlacklist)))

        