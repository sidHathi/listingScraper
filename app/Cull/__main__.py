from ..models.CullingModel import CullingModel
from ..models.TagModel import TagModel
from ..DBInterface import DBInterface
from .Culler import Culler

import sys
import asyncio

async def main():
    rentCullingModel: CullingModel = CullingModel(
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
    fbmCullingModel: CullingModel = CullingModel(
        targetVal='unavailable',
        tagMap= [
            TagModel(tagType='div', identifiers={
                'class': 'x78zum5 x1iyjqo2 x1n2onr6 xdt5ytf'
            }),
            TagModel(tagType='div', identifiers={
                'class': 'xyamay9 x1pi30zi x18d9i69 x1swvt13'
            }),
            TagModel(tagType='h1', identifiers={
                'class': 'x1heor9g x1qlqyl8 x1pd3egz x1a2a7pz x193iq5w xeuugli'
            })
        ],
        notFoundTag=None,
        expirationTimeInDays=5
    )
    cullingMap = {
        'facebook': fbmCullingModel,
        'rent.com': rentCullingModel
    }

    dbInterface: DBInterface = DBInterface()  
    culler: Culler = Culler(cullingMap, dbInterface)

    await culler.cullExpiredListings()

if (__name__ == '__main__'):
    sys.exit(asyncio.run(main()))



    