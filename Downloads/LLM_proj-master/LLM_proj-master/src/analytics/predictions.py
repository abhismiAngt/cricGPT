import pandas as pd
from data.db_loader import connect_db
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

def prepare_data():
    conn = connect_db()

    query = """
    SELECT
        d.match_id,
        m.season,
        m.venue,
        m.toss_winner,
        m.team1,
        m.team2,
        m.toss_decision,
        d.batting_team,
        SUM(total_runs) AS total_score
    FROM deliveries d
    JOIN matches m ON d.match_id = m.id
    WHERE d.inning = 1
    GROUP BY d.match_id, m.season, m.venue, m.toss_winner, m.team1, m.team2, m.toss_decision, d.batting_team;
    """

    df = pd.read_sql(query, conn)
    return df

def predict_total_score():
    df = prepare_data()

    df_encoded = pd.get_dummies(df.drop(columns=["match_id", "total_score"]))
    y = df["total_score"]

    X_train, X_test, y_train, y_test = train_test_split(df_encoded, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    error = mean_absolute_error(y_test, preds)

    return round(error, 2), model, X_train.columns.tolist()
def predict_for_input(season, venue, toss_winner, team1, team2, toss_decision, batting_team, model, encoder_cols):
    input_data = pd.DataFrame([{
        "season": season,
        "venue": venue,
        "toss_winner": toss_winner,
        "team1": team1,
        "team2": team2,
        "toss_decision": toss_decision,
        "batting_team": batting_team
    }])

    input_encoded = pd.get_dummies(input_data)

    for col in encoder_cols:
        if col not in input_encoded:
            input_encoded[col] = 0

    input_encoded = input_encoded[encoder_cols]

    prediction = model.predict(input_encoded)[0]
    return round(prediction, 2)
