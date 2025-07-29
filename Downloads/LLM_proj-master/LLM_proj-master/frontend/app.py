import streamlit as st

st.set_page_config(page_title="Cricket Stats GPT", layout="wide")

import sys, os, re
from matplotlib.figure import Figure
import pandas as pd

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from viz.charts            import bar_chart, line_chart, pie_chart
from analytics.comparisons import compare_players
from analytics.team        import season_win_counts, powerplay_scores
from agents.multitool_agent import get_multitool_agent
from data.db_loader        import connect_db

@st.cache_data
def get_reference_lists():
    conn = connect_db()
    teams      = pd.read_sql("SELECT DISTINCT team1      FROM matches", conn)["team1"].dropna().unique().tolist()
    seasons    = pd.read_sql("SELECT DISTINCT season     FROM matches", conn)["season"].dropna().unique().tolist()
    players    = pd.read_sql("SELECT DISTINCT batsman    FROM deliveries", conn)["batsman"].dropna().unique().tolist()
    venues     = pd.read_sql("SELECT DISTINCT venue      FROM matches", conn)["venue"].dropna().unique().tolist()
    cities     = pd.read_sql("SELECT DISTINCT city       FROM matches", conn)["city"].dropna().unique().tolist()
    match_ids  = pd.read_sql("SELECT DISTINCT id         FROM matches", conn)["id"].dropna().unique().tolist()
    dismissals = pd.read_sql("SELECT DISTINCT dismissal_kind FROM deliveries", conn)["dismissal_kind"].dropna().unique().tolist()
    conn.close()
    return teams, seasons, players, venues, cities, match_ids, dismissals

teams, seasons, players, venues, cities, match_ids, dismissals = get_reference_lists()

agent = get_multitool_agent()

st.title("🏏 Cricket Stats GPT")

with st.sidebar:
    with st.expander("📌 Reference Info (avoid typos)"):
        st.markdown("**Seasons:**");          st.text(", ".join(map(str, seasons)))
        st.markdown("**Teams:**");            st.text(", ".join(teams))
        st.markdown("**Players:**");          st.text(", ".join(players[:100]))
        st.markdown("**Venues:**");           st.text(", ".join(venues))
        st.markdown("**Cities:**");           st.text(", ".join(cities))
        st.markdown("**Match IDs:**");        st.text(", ".join(map(str, match_ids[:100])))
        st.markdown("**Dismissal Types:**");   st.text(", ".join(dismissals))

    with st.expander("🔧 Features & Examples"):
        st.markdown("**Supported Features:**")
        st.markdown(
            "- Player comparison\n"
            "- Top run scorers\n"
            "- Top wicket takers\n"
            "- Venue average score\n"
            "- Team wins per season\n"
            "- Powerplay runs per match\n"
            "- Win percentage\n"
            "- Match summary\n"
            "- Score prediction"
        )
        st.markdown("**Example Queries:**")
        example_map = {
            "Player comparison":           "compare between V Kohli vs S Dhawan",
            "Top run scorers":             "top run scorers 2015, 5",
            "Top wicket takers":           "top wicket takers 2016",
            "Venue average score":         "average match score at Wankhede Stadium",
            "Team wins per season":        "team wins per season Mumbai Indians",
            "Powerplay runs per match":    "powerplay runs Mumbai Indians, 2015",
            "Win percentage":              "win percentage Chennai Super Kings",
            "Match summary":               "summarize match 392200",
            "Score prediction":            "predict first innings score",
        }
        sel = st.selectbox("Pick an example", list(example_map.keys()))
        st.code(example_map[sel], language="text")

st.subheader("📥 SQL & Natural Language Query")
user_query = st.text_area(
    "Query",
    placeholder="Type a Query here",
    height=100,
)

if st.button("Run"):
    if not user_query.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Thinking..."):
            response = agent.invoke(user_query)

        st.markdown("### 🤖 Response")
        if isinstance(response, dict) and "output" in response:
            result = response["output"]
        else:
            result = response

        if (
            isinstance(result, list)
            and result
            and isinstance(result[0], dict)
            and "player" in result[0]
        ):
            df_comp = pd.DataFrame(result)
            st.write("### Player Comparison Data", df_comp)

            fig1 = bar_chart(
                df_comp, "player", "total_runs",
                title="Total Runs Comparison"
            )
            st.pyplot(fig1)

            fig2 = bar_chart(
                df_comp, "player", "strike_rate",
                title="Strike Rate Comparison"
            )
            st.pyplot(fig2)

        elif isinstance(result, Figure):
            st.pyplot(result)
        elif isinstance(result, list) and all(isinstance(o, Figure) for o in result):
            for fig in result:
                st.pyplot(fig)

        else:
            if isinstance(result, str):
                st.text(result)
            else:
                st.write(result)

st.markdown("---")
st.subheader("📊 Quick Charts")
chart_type = st.selectbox(
    "Choose a pre-built chart",
    [
        "Player Comparison",
        "Team Wins per Season",
        "Powerplay Runs per Match",
    ],
)
if chart_type == "Player Comparison":
    c1, c2 = st.columns(2)
    p1 = c1.selectbox("Player 1", players, key="qc_p1")
    p2 = c2.selectbox("Player 2", players, key="qc_p2")
    if st.button("Generate Player Comparison", key="qc_player"):
        df = compare_players(p1, p2)
        st.write(f"### {p1} vs {p2} — Total Runs")
        st.pyplot(bar_chart(df, "player", "total_runs"))
        st.write(f"### {p1} vs {p2} — Strike Rate")
        st.pyplot(bar_chart(df, "player", "strike_rate"))

elif chart_type == "Team Wins per Season":
    team = st.selectbox("Team", teams, key="qc_teamwins")
    if st.button("Generate Team Wins Chart", key="qc_team"):
        df = season_win_counts(team)
        st.write(f"### {team} Wins per Season")
        st.pyplot(line_chart(df, "season", "wins"))

elif chart_type == "Powerplay Runs per Match":
    c1, c2 = st.columns(2)
    team_pp   = c1.selectbox("Team", teams, key="qc_pp_team")
    season_pp = c2.selectbox("Season", seasons, key="qc_pp_season")
    if st.button("Generate Powerplay Chart", key="qc_pp"):
        df = powerplay_scores(team_pp, int(season_pp))
        st.write(f"### {team_pp} Powerplay Runs ({season_pp})")
        st.pyplot(line_chart(df, "match_id", "powerplay_runs"))
