from typing import TextIO
import ast
import json

def getFailureDictsFromLogFile(file: TextIO) -> list[dict[str, dict[str, int]]] | None:
    try:
        file.readline()
        webdriverString: str = file.readline()
        webdriverDict: dict[str, dict[str, int]] = ast.literal_eval(webdriverString)
        file.readline()
        tiemoutString: str = file.readline()
        timeoutDict: dict[str, dict[str, int]] = ast.literal_eval(tiemoutString)
        return [webdriverDict, timeoutDict]
    except Exception:
        return None
    
def buildBlackListFromFailureDicts(dicts: list[dict[str, dict[str, int]]]) -> dict[str, set[str]] | None:
    if len(dicts) < 2:
        return None
    
    blacklists: dict[str, set[str]] = {}
    timeoutDict: dict[str, dict[str, int]] = dicts[1]
    for key, val in timeoutDict.items():
        blacklists[key] = set()
        for driver, numFailures in val.items():
            if numFailures > 0:
                blacklists[key].add(driver)

    return blacklists

def encodeBlacklists(blacklists: dict[str, list[str]], file: TextIO):
    try:
        file.write(json.dumps(blacklists))
    except Exception as e:
        print(e)

def reconstituteBlacklist(file: TextIO) -> dict[str, set[str]] | None:
    try:
        raw: str = file.read()
        json: dict[str, list[str]] = ast.literal_eval(raw)
        parsed: dict[str, set[str]] = {}
        for key, val in json.items():
            parsed[key] = set(val)
        return parsed
    except Exception as e:
        print(e)
        return None

def buildBlacklist() -> dict[str, set[str]] | None:
    blacklistFile: TextIO = open('requestLog.log', 'r')
    requestLog: TextIO = open('blacklist.log', 'r')
    failureDicts: list[dict[str, dict[str, int]]] | None = getFailureDictsFromLogFile(requestLog)
    if failureDicts is None:
        return None
    logBlacklist: dict[str, set[str]] | None = buildBlackListFromFailureDicts(failureDicts)
    prevBlacklist: dict[str, set[str]] | None = reconstituteBlacklist(blacklistFile)

    if logBlacklist is None and prevBlacklist is None:
        return None
    elif logBlacklist is None:
        logBlacklist = {}
    elif prevBlacklist is None:
        prevBlacklist = {}

    assert logBlacklist is not None and prevBlacklist is not None
    blacklist: dict[str, set[str]] = {}
    for key, val in prevBlacklist.items():
        blacklist[key] = val
    for key, val in logBlacklist.items():
        if key not in blacklist:
            blacklist[key] = set()
        blacklist[key] = val.union(blacklist[key])

    blacklistFile.close()
    requestLog.close()
    return blacklist

