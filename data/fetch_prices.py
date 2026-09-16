#%%

import os 
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient

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


# %%
from db import get_engine

engine = get_engine()
with engine.connect() as conn:
    print("Verbindung erfolgreich!")

# %%
from load_to_db import upsert_day_ahead_prices

upsert_day_ahead_prices(df, engine)
print(f"{len(df)} Zeilen geschrieben.")
# %%
