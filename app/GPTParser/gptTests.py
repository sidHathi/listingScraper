from .listingInputs import rentListing
from .gptUtils import gptDataExtract

def parseAirbnbTest():
    inputType = 'rental listing from airbnb'
    features = 'rent per month, address, maximum lease duration in months, and number of bedrooms'
    format = '[rent, address, lease duration, bedrooms]'
    samplePageText = rentListing

    return gptDataExtract(
        input=samplePageText,
        inputType=inputType,
        features=features,
        outFormat=format
    )

