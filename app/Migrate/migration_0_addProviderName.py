import sys

from ..DBInterface import DBInterface
from ..utils.migrationUtils import isMigrationNecessary, isRollbackPossible
from ..constants import providerNames

migrationIndex: int = 0
newField: str = 'providerName'
description: str = 'Uses URLs to add provider names to each listing'

def executeMigration(dbInterface: DBInterface):
    if not isMigrationNecessary(dbInterface, migrationIndex):
        return

    urlIdPairs: list[dict[str, str]] = dbInterface.getListingUrls()
    for pair in urlIdPairs:
        id: str = pair['_id']
        url: str = pair['url']

        for providerName in providerNames:
            if providerName in url:
                dbInterface.updateListingField(id, newField, providerName)
                break

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