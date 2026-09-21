#%%

import os 
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
from fetch_entsoe import fetch_day_ahead_prices, fetch_load_forecast, fetch_wind_solar_forecast
from load_to_db import upsert_rows



load_dotenv()  # read env and make API key available

client = EntsoePandasClient(api_key=os.getenv("ENTSOE_API_KEY"))

start = pd.Timestamp("2024-01-01", tz="Europe/Berlin")
end = pd.Timestamp("2024-01-08", tz="Europe/Berlin")

prices = client.query_day_ahead_prices("DE_LU", start=start, end=end)
prices


# %%
df = prices.reset_index()
df.columns = ["timestamp", "price_eur_mwh"]
df["bidding_zone"] = "DE_LU"

print(df)


from db import get_engine

engine = get_engine()
with engine.connect() as conn:
    print("Verbindung erfolgreich!")


from load_to_db import upsert_day_ahead_prices

upsert_day_ahead_prices(df, engine)
print(f"{len(df)} Zeilen geschrieben.")


#Load

load_df = fetch_load_forecast(start, end)
load_df

#Wind_solar

gen_df = fetch_wind_solar_forecast(start, end)
gen_df
# %%


upsert_rows(df, engine, "day_ahead_prices",
            conflict_cols=["timestamp", "bidding_zone"], update_cols=["price_eur_mwh"])
upsert_rows(load_df, engine, "load_forecast",
            conflict_cols=["timestamp", "bidding_zone"], update_cols=["load_mw"])
upsert_rows(gen_df, engine, "generation_forecast",
            conflict_cols=["timestamp", "bidding_zone", "source"], update_cols=["generation_mw"])

print("All three tables written.")