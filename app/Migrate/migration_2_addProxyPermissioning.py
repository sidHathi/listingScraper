import sys
from typing import Any

from ..DBInterface import DBInterface
from ..utils.migrationUtils import isMigrationNecessary, isRollbackPossible

migrationIndex: int = 2
newField: str = 'hasProxyPermission'
description: str = 'Adds a new boolean field to each query that determines whether or not a given query should use proxy bandwidth to scrape listings'

def executeMigration(dbInterface: DBInterface):
    if not isMigrationNecessary(dbInterface, migrationIndex):
        return
    
    queries: list[dict[str, Any]] = dbInterface.getQueries()
    for query in queries:
        id: str = query['_id']
        proxyEnabledForOldQueries: bool = True

        if newField not in queries:
            dbInterface.updateQueryField(id, newField, proxyEnabledForOldQueries)

    dbInterface.addMigration(description, migrationIndex, [newField])

def rollBackMigration(dbInterface: DBInterface):
    if not isRollbackPossible(dbInterface, migrationIndex):
        return
    
    dbInterface.removeQueryField(newField)
    dbInterface.removeMigration(migrationIndex)

def main():
    args: list[str] = sys.argv

    dbInterface: DBInterface = DBInterface()
    if 'reverse' in args:
        rollBackMigration(dbInterface)
        return
    executeMigration(dbInterface)


if __name__ == '__main__':
    main()