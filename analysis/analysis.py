# %%
import pandas as pd
from data.db import get_engine
import matplotlib.pyplot as plt

engine = get_engine()

prices = pd.read_sql(
    "SELECT timestamp, price_eur_mwh FROM day_ahead_prices ORDER BY timestamp",
    engine,
    index_col="timestamp",
)
prices.head()

len(prices)
# %%
# %%
prices["month"] = prices.index.month
monthly_avg = prices.groupby("month")["price_eur_mwh"].mean()
monthly_avg.plot(kind="bar", title="Durchschnittlicher Day-Ahead-Preis pro Monat (2024)")
# %%


# %%
prices.index = prices.index.tz_convert("Europe/Berlin")

load = pd.read_sql(
    "SELECT timestamp, load_mw FROM load_forecast ORDER BY timestamp",
    engine, index_col="timestamp",
)
load.index = load.index.tz_convert("Europe/Berlin")

generation = pd.read_sql(
    "SELECT timestamp, source, generation_mw FROM generation_forecast ORDER BY timestamp",
    engine,
)
generation["timestamp"] = generation["timestamp"].dt.tz_convert("Europe/Berlin")

# %%
load_hourly = load["load_mw"].resample("1h").mean()

gen_wide = generation.pivot(index="timestamp", columns="source", values="generation_mw")
gen_hourly = gen_wide.resample("1h").mean()
gen_hourly["renewables_mw"] = gen_hourly.sum(axis=1)

market_df = pd.DataFrame({
    "price_eur_mwh": prices["price_eur_mwh"],
    "load_mw": load_hourly,
    "renewables_mw": gen_hourly["renewables_mw"],
})
market_df["residual_load_mw"] = market_df["load_mw"] - market_df["renewables_mw"]
market_df = market_df.dropna()

len(market_df)
# %%

# %%
negative_prices = market_df[market_df["price_eur_mwh"] < 0]
print(f"{len(negative_prices)} von {len(market_df)} Stunden mit negativem Preis ({len(negative_prices)/len(market_df)*100:.1f}%)")
print(negative_prices[["price_eur_mwh", "renewables_mw", "residual_load_mw"]].describe())
# %%
# %%
negative_prices.groupby(negative_prices.index.hour).size().plot(
    kind="bar", title="Negative Preise nach Uhrzeit"
)
plt.show()
# %%
# %%
gen_at_neg_prices = gen_hourly.loc[negative_prices.index]
gen_at_neg_prices.groupby(gen_at_neg_prices.index.hour)[["Solar", "Wind Onshore", "Wind Offshore"]].mean()
# %%
