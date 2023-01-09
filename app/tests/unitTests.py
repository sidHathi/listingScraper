from bs4 import BeautifulSoup
from geopy.geocoders import Nominatim, GoogleV3
from geopy.location import Location
from geopy.extra.rate_limiter import RateLimiter
from dotenv import dotenv_values

from ..models.TagModel import TagModel
from ..models.Query import Query
from ..interfaces.UrlService import UrlService
from ..Rent.RentUrlService import RentUrlService
from ..Zillow.ZillowUrlService import ZillowUrlService
from ..Apartments.ApartmentsUrlService import ApartmentsUrlService
from ..Airbnb.AirbnbUrlService import AirbnbUrlService
from ..Airbnb.AirbnbListingService import AirbnbListingService
from ..FBM.FBMUrlService import FBMUrlService
from ..enums import REType, LeaseTerm
from ..utils.scrapingUtils import followTagMap, findIntegerListMonths, findIntegerMonths
from ..constants import usStateToAbbrev
from ..interfaces.UrlService import UrlService
from ..interfaces.ListingService import ListingService
from ..models.ParsingModel import ParsingModel
from ..constants import rentSearchingTag, fbmSearchingTag, zillowSearchingTag, airbnbSearchingTag
from ..Scrape.Scraper import Scraper
from ..DBInterface import DBInterface
from ..RequestHub import RequestHub

from ..Zillow.ZillowListingService import ZillowListingService
from ..Zillow.ZillowUrlService import ZillowUrlService

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

def testZillowUrl1() -> bool:
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
        bedrooms=2,
        priceRange=[500, 4000],
        leaseTerm=LeaseTerm.LongTerm,
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

def testZillowUrl2() -> bool:
    testLocationStr = 'Seattle, WA'
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
        priceRange=[0, 4000],
        leaseTerm=LeaseTerm.ShortTerm,
        leaseDuration=6,
        pets=False,
        transit=False)

    urlService: UrlService = ZillowUrlService()
    url: str | None = urlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)
    return True


def testZillowUrl3() -> bool:
    testLocationStr = 'Boston, MA'
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
        bedrooms=2,
        priceRange=[0, 2000],
        leaseTerm=LeaseTerm.ShortTerm,
        leaseDuration=6,
        pets=True,
        transit=False)

    urlService: UrlService = ZillowUrlService()
    url: str | None = urlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)
    return True

def testZillowScrape() -> bool:
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
    
    dbInterface: DBInterface = DBInterface()
    requestHub: RequestHub = RequestHub()

    zillowUrlService: UrlService = ZillowUrlService()
    zillowListingService: ListingService = ZillowListingService()
    zillowParsingModel = ParsingModel(targetTag=zillowSearchingTag, requiresTagMap=False, listingService=zillowListingService)
    zillowScraper: Scraper = Scraper(
        urlString ='', 
        urlService=zillowUrlService, 
        listingService=zillowListingService,
        paginationModel=None, 
        parsingModel=zillowParsingModel, 
        dbInterface = dbInterface, 
        requestHub=requestHub,
        scrapeWithProxy=True,
        scrapeHeadlessly=False
    )

    zillowScraper.executeQuery(testQuery)

    return True

def testApartmentsUrl1() -> bool:
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
        priceRange=[0, 4000],
        leaseTerm=LeaseTerm.ShortTerm,
        leaseDuration=6,
        pets=True,
        transit=False
    )
    
    urlService: UrlService = ApartmentsUrlService()
    url: str | None = urlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)
    return True

def testAirbnbUrl1() -> bool:
    testLocationStr = 'Boston, MA'
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
        priceRange=[0, 4000],
        leaseTerm=LeaseTerm.ShortTerm,
        leaseDuration=6,
        pets=True,
        transit=False
    )
    
    urlService: UrlService = AirbnbUrlService()
    url: str | None = urlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)
    return True

def testAirbnbScrape() -> bool:
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
    
    dbInterface: DBInterface = DBInterface()
    requestHub: RequestHub = RequestHub()

    airbnbUrlService: UrlService = AirbnbUrlService()
    airbnbListingService: ListingService = AirbnbListingService()
    airbnbParsingModel = ParsingModel(targetTag=airbnbSearchingTag, requiresTagMap=False, listingService=airbnbListingService)
    airbnbScraper: Scraper = Scraper(
        urlString ='https://www.airbnb.com', 
        urlService=airbnbUrlService, 
        listingService=airbnbListingService,
        paginationModel=None, 
        parsingModel=airbnbParsingModel, 
        dbInterface = dbInterface, 
        requestHub=requestHub,
        scrapeWithProxy=False,
        scrapeHeadlessly=False
    )

    airbnbScraper.executeQuery(testQuery)

    return True

def testNYCQuery() -> bool:
    testLocationStr = '260 Broadway, Brooklyn, NY 10007, USA'
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
        priceRange=[0, 10000],
        leaseTerm=LeaseTerm.LongTerm,
        leaseDuration=12,
        pets=False,
        transit=False,
        hasProxyPermission=False)
    
    
    dbInterface: DBInterface = DBInterface()
    requestHub: RequestHub = RequestHub()

    airbnbUrlService: UrlService = AirbnbUrlService()
    airbnbListingService: ListingService = AirbnbListingService()
    airbnbParsingModel = ParsingModel(targetTag=airbnbSearchingTag, requiresTagMap=False, listingService=airbnbListingService)
    airbnbScraper: Scraper = Scraper(
        urlString ='https://www.airbnb.com', 
        urlService=airbnbUrlService, 
        listingService=airbnbListingService,
        paginationModel=None, 
        parsingModel=airbnbParsingModel, 
        dbInterface = dbInterface, 
        requestHub=requestHub,
        scrapeWithProxy=False,
        scrapeHeadlessly=False
    )

    airbnbScraper.executeQuery(testQuery)
    return True

def testUrlBuilders() -> bool:
    testLocationStr = 'Georgia Ave Petworth Station, District of Freedom#8573311~!#, Washington, DC 20036, USA'
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
        priceRange=[0, 10000],
        leaseTerm=LeaseTerm.LongTerm,
        leaseDuration=12,
        pets=False,
        transit=False,
        hasProxyPermission=False)
    
    
    dbInterface: DBInterface = DBInterface()
    requestHub: RequestHub = RequestHub()

    airbnbUrlService: UrlService = AirbnbUrlService()
    url: str | None = airbnbUrlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)

    rentUrlService: UrlService = RentUrlService()
    url: str | None = rentUrlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)

    zillowUrlService: UrlService = ZillowUrlService()
    url: str | None = zillowUrlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)

    aptsUrlService: UrlService = ApartmentsUrlService()
    url: str | None = aptsUrlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)

    fbmUrlService: UrlService = FBMUrlService()
    url: str | None = fbmUrlService.construct(testQuery)
    if url is None:
        print('url construct failed')
        return False
    print(url)
    return True
