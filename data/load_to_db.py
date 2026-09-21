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

def upsert_rows(df, engine, table: str, conflict_cols: list, update_cols: list) -> None:
    columns = list(df.columns)
    col_list = ", ".join(columns)
    placeholders = ", ".join(f":{c}" for c in columns)
    conflict_clause = ", ".join(conflict_cols)
    update_clause = ", ".join(f"{c} = EXCLUDED.{c}" for c in update_cols)

    sql = text(f"""
        INSERT INTO {table} ({col_list})
        VALUES ({placeholders})
        ON CONFLICT ({conflict_clause})
        DO UPDATE SET {update_clause};
    """)

    with engine.begin() as conn:
        for row in df.to_dict(orient="records"):
            conn.execute(sql, row)




