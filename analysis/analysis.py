# %%
import pandas as pd
from db import get_engine

engine = get_engine()

prices = pd.read_sql(
    "SELECT timestamp, price_eur_mwh FROM day_ahead_prices ORDER BY timestamp",
    engine,
    index_col="timestamp",
)
prices.head()

len(prices)