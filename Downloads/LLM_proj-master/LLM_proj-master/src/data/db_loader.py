import pandas as pd
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

def connect_db():
    return pymysql.connect(
        host="localhost",
        user="root",
        password=os.getenv("MYSQL_PASSWORD"),
        database="cricstats"
    )

def load_matches_to_db(csv_path):
    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")
    df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})


    conn = connect_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT IGNORE INTO matches (
        id, season, city, date, team1, team2, toss_winner, toss_decision,
        result, dl_applied, winner, win_by_runs, win_by_wickets,
        player_of_match, venue, umpire1, umpire2, umpire3
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for row in df.itertuples(index=False):
        cursor.execute(insert_query, tuple(row))

    conn.commit()
    conn.close()
    print(f" Loaded {len(df)} rows into matches")


def load_deliveries_to_db(csv_path):
    df = pd.read_csv(csv_path)
    df.rename(columns={"over": "over_balled"}, inplace=True)
    df = df.replace({pd.NA: None, pd.NaT: None, float('nan'): None})

    conn = connect_db()
    cursor = conn.cursor()

    insert_query = """
    INSERT INTO deliveries (
        match_id, inning, batting_team, bowling_team, over_balled, ball,
        batsman, non_striker, bowler, is_super_over, wide_runs, bye_runs,
        legbye_runs, noball_runs, penalty_runs, batsman_runs, extra_runs,
        total_runs, player_dismissed, dismissal_kind, fielder
    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """

    for row in df.itertuples(index=False, name=None):
        cursor.execute(insert_query, row)

    conn.commit()
    conn.close()
    print(f" Loaded {len(df)} rows into deliveries")
