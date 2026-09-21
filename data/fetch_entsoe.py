#%%

import os
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

load_dotenv()
API_KEY = os.getenv("ENTSOE_API_KEY")
BIDDING_ZONE = "DE_LU"


def fetch_day_ahead_prices(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    client = EntsoePandasClient(api_key=API_KEY)
    prices = client.query_day_ahead_prices(BIDDING_ZONE, start=start, end=end)
    df = prices.reset_index()
    df.columns = ["timestamp", "price_eur_mwh"]
    df["bidding_zone"] = BIDDING_ZONE
    return df


def fetch_load_forecast(start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    client = EntsoePandasClient(api_key=API_KEY)
    load = client.query_load_forecast(BIDDING_ZONE, start=start, end=end)
    df = load.reset_index()
    df.columns = ["timestamp", "load_mw"]
    df["bidding_zone"] = BIDDING_ZONE
    return df


def fetch_wind_solar_forecast (start: pd.Timestamp, end: pd.Timestamp) -> pd.DataFrame:
    """
    Use melt() for changing formats -> Problem lies in the format of type of production
    Due to the different data availabliity there might be compability issues for different bidding zones
    in the data bank.
    For handling purposes use pivot() to re-change format
    """
    client = EntsoePandasClient(api_key = API_KEY)
    generation = client.query_intraday_wind_and_solar_forecast(BIDDING_ZONE, start= start, end=end)

    df = generation.rename_axis("timestamp").reset_index()
    df = df.melt(id_vars="timestamp", var_name= "source", value_name= "generation_mw") #
    df["bidding_zone"] = BIDDING_ZONE
    return df



# %%
