from ..models.CullingModel import CullingModel
from ..models.TagModel import TagModel
from ..DBInterface import DBInterface
from .Culler import Culler

import sys
import asyncio

async def main():
    cullingModel: CullingModel = CullingModel(
        targetVal='Currently Unavailable',
        tagMap= [
            TagModel(
                tagType= 'div',
                identifiers= {'data-tid': 'sticky-lead-form'}
            ),
            TagModel(
                tagType= None,
                identifiers= {'data-tid': 'lead-form-header'}
            )
        ],
        notFoundTag=TagModel(
            tagType= None,
            identifiers= {'data-tid': 'search-results-page'}
        ),
        expirationTimeInDays=5
    )
    dbInterface: DBInterface = DBInterface()  
    culler: Culler = Culler(cullingModel, dbInterface)

    await culler.cullExpiredListings()

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))



    