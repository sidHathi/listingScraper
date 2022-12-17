from bs4 import BeautifulSoup
from .models.TagModel import TagModel
from .utils.scrapingUtils import followTagMap, findIntegerListMonths, findIntegerMonths

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