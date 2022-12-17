from typing import Any

def reverseDict(keyVals: dict[Any, Any]) -> dict[Any, Any]:
    return dict(zip(keyVals.values(), keyVals.keys()))