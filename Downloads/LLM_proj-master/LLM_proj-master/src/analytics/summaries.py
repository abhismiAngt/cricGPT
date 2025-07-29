import pandas as pd
from data.db_loader import connect_db
from llm.gemini_utils import load_gemini_model

model = load_gemini_model()

def generate_match_summary(match_id: int):
    conn = connect_db()

    match_df = pd.read_sql(f"SELECT * FROM matches WHERE id = {match_id};", conn)
    if match_df.empty:
        return f"⚠️ Match ID {match_id} not found in the database."

    match_info = match_df.iloc[0]

    team1 = match_info["team1"]
    team2 = match_info["team2"]
    winner = match_info["winner"]
    date = match_info["date"]
    venue = match_info["venue"]
    player_of_match = match_info["player_of_match"]
    season = match_info["season"]

    top_batsman_sql = f"""
    SELECT batsman, SUM(batsman_runs) AS runs
    FROM deliveries
    WHERE match_id = {match_id}
    GROUP BY batsman
    ORDER BY runs DESC
    LIMIT 1;
    """
    top_batsman = pd.read_sql(top_batsman_sql, conn).iloc[0]

    top_bowler_sql = f"""
    SELECT bowler, COUNT(*) AS wickets
    FROM deliveries
    WHERE match_id = {match_id} AND player_dismissed IS NOT NULL
    GROUP BY bowler
    ORDER BY wickets DESC
    LIMIT 1;
    """
    top_bowler = pd.read_sql(top_bowler_sql, conn).iloc[0]

    prompt = f"""
Generate a 3-4 sentence IPL match summary for match ID {match_id}.
Teams: {team1} vs {team2}
Date: {date}, Venue: {venue}, Season: {season}
Winner: {winner}, Player of the Match: {player_of_match}
Top batsman: {top_batsman['batsman']} ({top_batsman['runs']} runs)
Top bowler: {top_bowler['bowler']} ({top_bowler['wickets']} wickets)
Do not include any analysis or speculation. Be concise.
"""

    response = model.generate_content(prompt)
    return response.text.strip()
