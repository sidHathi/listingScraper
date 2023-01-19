from typing import TextIO
import ast
import json

def getTimeoutDictFromLogFile(file: TextIO) -> dict[str, dict[str, int]] | None:
    try:
        file.readline()
        webdriverString: str = file.readline()
        file.readline()
        timeoutString: str = file.readline()
        print('timeout string ' + str(timeoutString))
        timeoutDict: dict[str, dict[str, int]] = ast.literal_eval(timeoutString)
        print('timeout dict ' + str(timeoutDict))

        return timeoutDict
    except Exception as e:
        print('EXCEPTION: ' + str(e))
        return None
    
def buildBlackListFromFailureDict(timeoutDict: dict[str, dict[str, int]]) -> dict[str, set[str]] | None:
    blacklists: dict[str, set[str]] = {}
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
    requestLog: TextIO = open('requestLog.log', 'r')
    blacklistFile: TextIO = open('blacklist.log', 'r')
    failureDict: dict[str, dict[str, int]] | None = getTimeoutDictFromLogFile(requestLog)
    if failureDict is None:
        print('no failure dict found')
        return None
    logBlacklist: dict[str, set[str]] | None = buildBlackListFromFailureDict(failureDict)
    prevBlacklist: dict[str, set[str]] | None = reconstituteBlacklist(blacklistFile)

    if logBlacklist is None and prevBlacklist is None:
        'blacklist reconstitute failed'
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

