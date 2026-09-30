#%%

import os 
import pandas as pd
from dotenv import load_dotenv
from entsoe import EntsoePandasClient
from data.fetch_entsoe import fetch_day_ahead_prices, fetch_load_forecast, fetch_wind_solar_forecast
from data.load_to_db import upsert_rows



load_dotenv()  # read env and make API key available

client = EntsoePandasClient(api_key=os.getenv("ENTSOE_API_KEY"))

start = pd.Timestamp("2024-01-01", tz="Europe/Berlin")
end = pd.Timestamp("2025-01-01", tz="Europe/Berlin")

prices = client.query_day_ahead_prices("DE_LU", start=start, end=end)
prices



df = prices.reset_index()
df.columns = ["timestamp", "price_eur_mwh"]
df["bidding_zone"] = "DE_LU"

print(df)


from data.db import get_engine

engine = get_engine()
with engine.connect() as conn:
    print("Verbindung erfolgreich!")


from data.load_to_db import upsert_day_ahead_prices

upsert_day_ahead_prices(df, engine)
print(f"{len(df)} Zeilen geschrieben.")


#Load

load_df = fetch_load_forecast(start, end)
load_df

#Wind_solar

gen_df = fetch_wind_solar_forecast(start, end)
gen_df



upsert_rows(df, engine, "day_ahead_prices",
            conflict_cols=["timestamp", "bidding_zone"], update_cols=["price_eur_mwh"])
upsert_rows(load_df, engine, "load_forecast",
            conflict_cols=["timestamp", "bidding_zone"], update_cols=["load_mw"])
upsert_rows(gen_df, engine, "generation_forecast",
            conflict_cols=["timestamp", "bidding_zone", "source"], update_cols=["generation_mw"])

print("All three tables written.")

load_df["timestamp"].diff().value_counts()

load_hourly = load_df.set_index("timestamp")["load_mw"].resample("1h").mean()

gen_wide = gen_df.pivot(index="timestamp", columns="source", values="generation_mw")
gen_hourly = gen_wide.resample("1h").mean()
gen_hourly["renewables_mw"] = gen_hourly.sum(axis=1)

gen_hourly.head()

residual_load = load_hourly - gen_hourly["renewables_mw"]
residual_load.name = "residual_load_mw"
residual_load.head()

# 
price_hourly = df.set_index("timestamp")["price_eur_mwh"]

market_df = pd.DataFrame({
    "price_eur_mwh": price_hourly,
    "load_mw": load_hourly,
    "renewables_mw": gen_hourly["renewables_mw"],
})
market_df["residual_load_mw"] = market_df["load_mw"] - market_df["renewables_mw"]
market_df.head()
# %%

#####-------------------------------------####
#####---Small analysis--------------------####
#####-------------------------------------####

market_df.isna().sum()
# %%
market_df[market_df.isna().any(axis=1)]

# %%
market_df.loc["2024-12-11":"2024-12-13"][["price_eur_mwh", "renewables_mw", "residual_load_mw"]]
# %%
market_df_clean = market_df.dropna()
print(f"{len(market_df) - len(market_df_clean)} von {len(market_df)} Zeilen wegen fehlender Werte entfernt.")
# %%

# %%
market_df["hour"] = market_df.index.hour
hourly_avg = market_df.groupby("hour")[["price_eur_mwh", "residual_load_mw"]].mean()
hourly_avg.plot(subplots=True, title=["Durchschnittspreis nach Uhrzeit", "Durchschnittliche Residuallast nach Uhrzeit"], legend=False)
# %%
