import pandas as pd
from data.db_loader import connect_db

def season_win_counts(team: str):
    sql = f"""
    SELECT season, COUNT(*) AS wins
    FROM matches
    WHERE winner = '{team}'
    GROUP BY season
    ORDER BY season;
    """
    return pd.read_sql(sql, connect_db())

def powerplay_scores(team: str, season: int):
    sql = f"""
    SELECT match_id, SUM(total_runs) AS powerplay_runs
    FROM deliveries
    JOIN matches ON deliveries.match_id = matches.id
    WHERE deliveries.batting_team = '{team}' AND matches.season = {season} AND deliveries.over_balled <= 6
    GROUP BY match_id
    ORDER BY match_id;
    """
    return pd.read_sql(sql, connect_db())

def win_percentage(team: str):
    sql = f"""
    SELECT 
        COUNT(*) AS total_matches,
        SUM(CASE WHEN winner = '{team}' THEN 1 ELSE 0 END) AS wins,
        ROUND(100.0 * SUM(CASE WHEN winner = '{team}' THEN 1 ELSE 0 END) / COUNT(*), 2) AS win_percent
    FROM matches
    WHERE team1 = '{team}' OR team2 = '{team}';
    """
    return pd.read_sql(sql, connect_db())
