#%%
from sqlalchemy import text
from db import get_engine

UPSERT_SQL = text("""
    INSERT INTO day_ahead_prices (timestamp, bidding_zone, price_eur_mwh)
    VALUES (:timestamp, :bidding_zone, :price_eur_mwh)
    ON CONFLICT (timestamp, bidding_zone)
    DO UPDATE SET price_eur_mwh = EXCLUDED.price_eur_mwh;
""")

def upsert_day_ahead_prices(df, engine):
    with engine.begin() as conn:
        for row in df.to_dict(orient="records"):
            conn.execute(UPSERT_SQL, row)
# %%
