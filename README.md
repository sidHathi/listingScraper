#### Siddharth Hathi 2022

## The Listing Scraper

*Code Documentation still in progress*

This repository is one part of a housing aggregator web service for students. Its purpose is to scrape rental listings across multiple public listing websites and store them in a mongodb database collection. It also contains additional functionality to review listings and cull expired/old ones, and to migrate the database schema when additional fields are added/removed.

### Scrape

The [Scrape](app/Scrape) submodule is where the centralized scraper lives. Running it will begin the process of scraping listings across all currently supported listing providers based on queries described in the MongoDB database.

#### Usage:
To install dependencies:

```python
pip install -r requirements.txt
```

To run the scraper:

```python
python3 -m app.Scrape
```

### Cull

The [Cull](app/Cull) submodule is where the Culler lives. The Culler looks at every listing currently stored in the database and evaluates each one to determine whether it's still available to rent. It removes expired listings.

#### Usage:
To install dependencies:

```python
pip install -r requirements.txt
```

To run the culler:

```python
python3 -m app.Cull
```
