from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim, GoogleV3
from geopy.location import Location
from geopy.extra.rate_limiter import RateLimiter
from dotenv import dotenv_values

from ..models.TagModel import TagModel
from ..models.Query import Query
from ..interfaces.UrlService import UrlService
from ..Zillow.ZillowUrlService import ZillowUrlService
from ..enums import REType, LeaseTerm
from ..utils.scrapingUtils import followTagMap, findIntegerListMonths, findIntegerMonths
from ..constants import usStateToAbbrev

config = dotenv_values('.env')

def testTagMapFollow() -> bool:
    testHtml = '''
        <div data-tag='fakeTag'>
            <ul>
                <h2 name='fakeName'>testResult</h2>
            </ul>
        </div>
        <div data-tag='fakeTag'>
            <p>fake</p>
        </div>
    '''
    testTagMap: list[TagModel] = [
        TagModel(tagType='div', identifiers={'data-tag': 'fakeTag'}),
        TagModel(tagType='ul', identifiers={}),
        TagModel(tagType='h2', identifiers={'name': 'fakeName'})
    ]
    expectedVal: str = 'testResult'
    testDom = BeautifulSoup(testHtml, 'html.parser')

    matchingTags: list[BeautifulSoup] = followTagMap(testTagMap, testDom)
    assert(len(matchingTags) == 1)
    assert(matchingTags[0].text == expectedVal)

    return True

def testRegexMatching() -> bool:
    sampleText = 'the lease terms are 1, 2, 3, 4, 5 and 6 months. that is all. maybe 8 months too'
    extract: list[int] | None = findIntegerListMonths(sampleText)
    # print(extract)

    assert(extract != None)
    assert(len(extract) == 7)

    simpleExtract: list[int] | None = findIntegerMonths(sampleText)
    assert(simpleExtract is not None)
    assert(len(simpleExtract) == 2)

    return True

def testZillowUrl() -> bool:
    testLocationStr = 'San Francisco, CA'
    geocoder = GoogleV3(api_key=config['GOOGLE_MAPS_API_KEY'])
    geocode = RateLimiter(geocoder.geocode, min_delay_seconds=1, return_value_on_exception=None)
    encoded = geocode(testLocationStr)
    if encoded is None:
        print('location encode failed')
        return False

    testQuery: Query = Query(
        name='unitTestQuery',
        location=encoded,
        reType=REType.Apartment,
        bedrooms=1,
        priceRange=[500, 4000],
        leaseTerm=LeaseTerm.ShortTerm,
        leaseDuration=None,
        pets=False,
        transit=False)

    urlService: UrlService = ZillowUrlService()
    url: str | None = urlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)
    return True