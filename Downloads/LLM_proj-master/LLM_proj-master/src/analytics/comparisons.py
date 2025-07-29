import pandas as pd
from data.db_loader import connect_db

def compare_players(player1: str, player2: str):
    p1 = player1.strip().strip("'\"")
    p2 = player2.strip().strip("'\"")

    p1 = p1.replace("'", "''")
    p2 = p2.replace("'", "''")

    sql = f"""
    SELECT
        batsman      AS player,
        COUNT(*)     AS innings,
        SUM(batsman_runs)                                   AS total_runs,
        SUM(CASE WHEN batsman_runs = 4 THEN 1 ELSE 0 END)    AS fours,
        SUM(CASE WHEN batsman_runs = 6 THEN 1 ELSE 0 END)    AS sixes,
        COUNT(ball)                                         AS balls_faced
    FROM deliveries
    WHERE batsman IN ('{p1}', '{p2}')
    GROUP BY batsman
    """
    df = pd.read_sql(sql, connect_db())
    df["strike_rate"] = (df["total_runs"] / df["balls_faced"]) * 100
    return df.round(2)
