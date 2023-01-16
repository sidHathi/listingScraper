import sys
from typing import Any
import random

from ..DBInterface import DBInterface
from ..utils.migrationUtils import isMigrationNecessary, isRollbackPossible

migrationIndex: int = 1
newField: str = 'pageRank'
description: str = 'Assigns random page ranks to pages without page ranks'

def executeMigration(dbInterface: DBInterface):
    if not isMigrationNecessary(dbInterface, migrationIndex):
        return

    listings: list[dict[str, Any]] = dbInterface.getCompleteListingDicts()
    for listing in listings:
        id: str = listing['_id']
        pageRank: int = random.randint(1, 101)

        if 'pageRank' not in listing:
            dbInterface.updateListingField(id, newField, pageRank)

    dbInterface.addMigration(description, migrationIndex, [newField])

def rollBackMigration(dbInterface: DBInterface):
    if not isRollbackPossible(dbInterface, migrationIndex):
        return
    
    dbInterface.removeListingField(newField)
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