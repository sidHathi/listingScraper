from pydantic import BaseModel

class EventMetric(BaseModel):
    total: int = 0
    successes: int = 0
    failures: int = 0

    def addSuccess(self):
        self.total += 1
        self.successes += 1

    def addFailure(self):
        self.failures += 1
        self.total += 1