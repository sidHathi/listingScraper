from typing import Any
from dotenv import dotenv_values
import openai
from .gptConstants import gptModelName

config = dotenv_values(".env")

def setAPIKey():
    if 'OPENAI_SECRET_KEY' not in config:
        return None
    
    openai.api_key = config['OPENAI_SECRET_KEY']

def getGptModels():
    setAPIKey()
    return openai.Model.list()

def makeGTPQuery(prompt: str, temperature: float):
    setAPIKey()
    response: Any = openai.Completion.create(
        model=gptModelName,
        prompt=prompt, 
        temperature=temperature,
        max_tokens=2000
    )
    if response.choices is not None and len(response.choices) > 0:
        return response.choices[0].text
    return None
    
def gptDataExtract(input: str, inputType: str, features: str, outFormat: str):
    prompt = f'extract the following data from this {inputType}: {features} and return it in the following format: {outFormat} \n {input}';
    return makeGTPQuery(prompt, 0)

def parseRentalListing(providerName: str, pageText: str) -> dict[str, str] | None:
    inputType = f'rental listing from {providerName}'
    features = 'rent per month, address, maximum lease duration in months, and number of bedrooms'
    format = '[rent, address, lease duration, bedrooms]'
    samplePageText = pageText

    gptResponse: str | None = gptDataExtract(
        input=samplePageText,
        inputType=inputType,
        features=features,
        outFormat=format
    )
    if gptResponse is None: return None

    splitResponse: list[str] = gptResponse[1:-1].split(', ')
    if len(splitResponse) < 4: return None
    return {
        'price': splitResponse[0],
        'address': splitResponse[1],
        'leaseDuration': splitResponse[2],
        'bedrooms': splitResponse[3],        
    }
