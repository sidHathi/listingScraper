from ..DBInterface import DBInterface

def isMigrationNecessary(dbInterface: DBInterface, index: int) -> bool:
    previousMigrationIndices: list[int] = dbInterface.getMigrationIndices()
    if len(previousMigrationIndices) < 1:
        return True

    latestMigrationIndex: int = max(previousMigrationIndices)
    if index < latestMigrationIndex:
        return False # this means you cannot redo previously rolled back migrations
    return True

def isRollbackPossible(dbInterface: DBInterface, index: int) -> bool:
    previousMigrationIndices: set[int] = set(dbInterface.getMigrationIndices())
    if len(previousMigrationIndices) < 1:
        return False

    if index in previousMigrationIndices:
        return True
    return False