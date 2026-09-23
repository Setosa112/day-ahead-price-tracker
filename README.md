# Day Ahead Price Tracker

Small project to prepare for my master thesis about trading strategies on the day-ahead and intra-day markets.
Loads Day-ahead electricity prices via Entsoe Transparency plattform.

## Setup

1. Activate conda env via "conda activate quant"
2. create .env Data with Entsoe API key and Database URL
3. Start Databank: docker compose up -d
4. Install project editable: pip install -e


## Project Structure

- data/ - load the data from Entsoe, Databank connection, upsert-logik
- analysis/ - explorative analysis of market data
- sql/schema.sql - databank schema


## Results

- **Seasonality**: remarkably high prices in November/December 2024 due to dark lull events (pricing peaks  over 900€/Mwh)
- **Duck Curve**: Daily patterns follow nearly identical form with midday lows and evening peaks
- **Negative Prices**: approx. 5.2% of the hours with two reasons - mid day solar driven and nighttime wind driven

## Status

- [x] Project-Setup (Git, env, .gitignore)
- [x] First data call
- [x] Explorative Analysis

