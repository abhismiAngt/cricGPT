import pandas as pd
from data.db_loader import connect_db

def top_run_scorers(season: int, limit: int = 5):
    sql = f"""
    SELECT d.batsman, SUM(d.batsman_runs) AS total_runs
    FROM deliveries d
    JOIN matches m ON d.match_id = m.id
    WHERE m.season = {season}
    GROUP BY d.batsman
    ORDER BY total_runs DESC
    LIMIT {limit};
    """
    return pd.read_sql(sql, connect_db())
def top_wicket_takers(season: int = None, team: str = None, limit: int = 5):
    where = ["player_dismissed IS NOT NULL"]
    if season:
        where.append(f"m.season = {season}")
    if team:
        where.append(f"d.bowling_team = '{team}'")
    where_clause = " AND ".join(where)

    sql = f"""
    SELECT d.bowler, COUNT(*) AS wickets
    FROM deliveries d
    JOIN matches m ON d.match_id = m.id
    WHERE {where_clause}
    GROUP BY d.bowler
    ORDER BY wickets DESC
    LIMIT {limit};
    """
    return pd.read_sql(sql, connect_db())
def average_match_score(venue: str):
    sql = f"""
    SELECT AVG(runs_per_match) AS avg_score
    FROM (
        SELECT match_id, SUM(total_runs) AS runs_per_match
        FROM deliveries
        JOIN matches ON deliveries.match_id = matches.id
        WHERE venue = '{venue}'
        GROUP BY match_id
    ) AS sub;
    """
    return pd.read_sql(sql, connect_db())
