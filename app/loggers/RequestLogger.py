from typing import TextIO
from urllib.parse import urlparse

class RequestLogger:
    def __init__(self, logFile: TextIO | None = None):
        self.logFile = logFile
        self.webDriverFailures: dict[str, dict[str, int]] = {}
        self.timeoutFailures: dict[str, dict[str, int]] = {}
        self.genericFailures: dict[str, dict[str, int]] = {}
        self.proxyFailures: int = 0
        self.nonProxyFailures: int = 0

    def addFailureToDict(self, dict: dict[str, dict[str, int]], userAgent: str, url: str, proxyUse: bool):
        domain: str = urlparse.urlparse(url).netloc
        if domain not in dict:
            dict[domain] = {f'{userAgent}': 0}

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

        