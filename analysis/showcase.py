# %% [markdown]
# # Day-Ahead Price Tracker – Zentrale Ergebnisse
#
# Analyse von Day-Ahead-Preisen, Last- und Erzeugungsprognosen für die
# deutsch-luxemburgische Bidding Zone (DE_LU), Jahr 2024.

# %%
import pandas as pd
import matplotlib.pyplot as plt
from data.db import get_engine

engine = get_engine()

prices = pd.read_sql("SELECT timestamp, price_eur_mwh FROM day_ahead_prices ORDER BY timestamp", engine, index_col="timestamp")
prices.index = prices.index.tz_convert("Europe/Berlin")

load = pd.read_sql("SELECT timestamp, load_mw FROM load_forecast ORDER BY timestamp", engine, index_col="timestamp")
load.index = load.index.tz_convert("Europe/Berlin")

generation = pd.read_sql("SELECT timestamp, source, generation_mw FROM generation_forecast ORDER BY timestamp", engine)
generation["timestamp"] = generation["timestamp"].dt.tz_convert("Europe/Berlin")

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

# %% [markdown]
# ## Saisonalität: Dunkelflauten im November/Dezember 2024

# %%
market_df["month"] = market_df.index.month
market_df.groupby("month")["price_eur_mwh"].mean().plot(
    kind="bar", title="Durchschnittlicher Day-Ahead-Preis pro Monat (2024)"
)
plt.ylabel("€/MWh")
plt.show()

# %% [markdown]
# ## Duck Curve: Preis und Residuallast im Tagesverlauf

# %%
market_df["hour"] = market_df.index.hour
market_df.groupby("hour")[["price_eur_mwh", "residual_load_mw"]].mean().plot(
    subplots=True,
    title=["Durchschnittspreis nach Uhrzeit", "Durchschnittliche Residuallast nach Uhrzeit"],
    legend=False,
)
plt.show()

# %% [markdown]
# ## Negative Preise: zwei unterschiedliche Ursachen (Solar tagsüber, Wind nachts)

# %%
negative_prices = market_df[market_df["price_eur_mwh"] < 0]
share = len(negative_prices) / len(market_df) * 100
print(f"{len(negative_prices)} von {len(market_df)} Stunden mit negativem Preis ({share:.1f}%)")

negative_prices.groupby(negative_prices.index.hour).size().plot(
    kind="bar", title="Negative Preise nach Uhrzeit"
)
plt.show()
# %%
