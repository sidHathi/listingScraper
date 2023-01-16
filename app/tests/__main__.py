from ..models.Query import Query
from .unitTests import testZillowUrl1, testZillowUrl2, testZillowUrl3, testZillowScrape, testApartmentsUrl1, testAirbnbUrl1, testAirbnbScrape, testNYCQuery, testUrlBuilders, runQueryOnProvider, getTestQuery

if __name__ == '__main__':
    print(testZillowUrl1())
    print(testZillowUrl2())
    print(testZillowUrl3())
    print(testApartmentsUrl1())
    print(testAirbnbUrl1())
    # print(testAirbnbScrape())
    # print(testZillowScrape())
    # print(testNYCQuery())
    print(testUrlBuilders())

    testQuery: Query | None = getTestQuery('New York City, NY')
    providerName: str = 'airbnb'
    if testQuery is not None:
        runQueryOnProvider(testQuery, providerName)
