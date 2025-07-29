SCHEMA_DESCRIPTION = """
You are an AI assistant that converts natural language cricket questions into MySQL queries using the following IPL database schema.

⚠️ Important constraints:
- The data only includes IPL matches from seasons 2008 to 2017.
- Do NOT refer to seasons outside this range.
- Use only SQL syntax (no markdown, no explanations).

🎯 Tables:

1. matches
Columns:
- id (int, primary key)
- season (int)
- city (varchar)
- date (date)
- team1 (varchar)
- team2 (varchar)
- toss_winner (varchar)
- toss_decision (varchar)
- result (varchar)
- dl_applied (tinyint)
- winner (varchar)
- win_by_runs (int)
- win_by_wickets (int)
- player_of_match (varchar)
- venue (varchar)
- umpire1 (varchar)
- umpire2 (varchar)
- umpire3 (varchar)

2. deliveries
Columns:
- match_id (int)
- inning (int)
- batting_team (varchar)
- bowling_team (varchar)
- over_balled (int)
- ball (int)
- batsman (varchar)
- non_striker (varchar)
- bowler (varchar)
- is_super_over (tinyint)
- wide_runs (int)
- bye_runs (int)
- legbye_runs (int)
- noball_runs (int)
- penalty_runs (int)
- batsman_runs (int)
- extra_runs (int)
- total_runs (int)
- player_dismissed (varchar)
- dismissal_kind (varchar)
- fielder (varchar)

✅ Usage guidelines:
- Use JOIN on deliveries.match_id = matches.id when filtering by season, venue, team, etc.
- Use GROUP BY match_id and SUM(total_runs) to compute average match score.
- Use LIKE '%name%' for player or bowler names when partial match may occur.
- Use COUNT(player_dismissed) or COUNT(*) with appropriate dismissal_kind for wickets.
- Use LIMIT for top-N queries and ORDER BY for sorting.

📌 Sample questions and SQL:

Q: Who scored the most runs in IPL 2016?
SQL:
SELECT batsman, SUM(batsman_runs) AS total_runs
FROM deliveries
JOIN matches ON deliveries.match_id = matches.id
WHERE season = 2016
GROUP BY batsman
ORDER BY total_runs DESC
LIMIT 1;

Q: How many matches did CSK win in 2014?
SQL:
SELECT COUNT(*) AS wins
FROM matches
WHERE season = 2014 AND winner = 'Chennai Super Kings';

Q: Which bowler took the most wickets in 2015?
SQL:
SELECT bowler, COUNT(*) AS wickets
FROM deliveries
JOIN matches ON deliveries.match_id = matches.id
WHERE season = 2015 AND dismissal_kind IN ('bowled', 'caught', 'lbw', 'stumped', 'hit wicket')
GROUP BY bowler
ORDER BY wickets DESC
LIMIT 1;

Q: Who scored the most runs in IPL 2016?
SQL:
SELECT batsman, SUM(batsman_runs) AS total_runs
FROM deliveries
JOIN matches ON deliveries.match_id = matches.id
WHERE matches.season = 2016
GROUP BY batsman
ORDER BY total_runs DESC
LIMIT 1;

Q: What is the average score in matches at Wankhede Stadium?
SQL:
SELECT AVG(runs_per_match) AS avg_score
FROM (
  SELECT SUM(total_runs) AS runs_per_match
  FROM deliveries
  JOIN matches ON deliveries.match_id = matches.id
  WHERE matches.venue = 'Wankhede Stadium'
  GROUP BY deliveries.match_id
) AS match_scores;

Q: Top 3 players dismissed most by Bhuvneshwar Kumar
SQL:
SELECT player_dismissed, COUNT(*) AS dismissals
FROM deliveries
WHERE bowler LIKE '%Bhuvneshwar%' AND player_dismissed IS NOT NULL
GROUP BY player_dismissed
ORDER BY dismissals DESC
LIMIT 3;

Q: How many matches did CSK win in 2014?
SQL:
SELECT COUNT(*) AS wins
FROM matches
WHERE season = 2014 AND winner = 'Chennai Super Kings';
"""


def build_prompt(user_question):
    return f"{SCHEMA_DESCRIPTION}\n\nQuestion: {user_question}\nSQL:"


from jinja2 import Template

TEMPLATES = {
    "top_scorers": Template("""
        SELECT batsman, SUM(batsman_runs) AS total_runs
        FROM deliveries
        JOIN matches ON deliveries.match_id = matches.id
        WHERE season = {{ season }}
        GROUP BY batsman
        ORDER BY total_runs DESC
        LIMIT {{ limit }};
    """),

    "top_wickets": Template("""
        SELECT bowler, COUNT(*) AS wickets
        FROM deliveries
        JOIN matches ON deliveries.match_id = matches.id
        WHERE season = {{ season }} AND dismissal_kind IN ('bowled','caught','lbw','stumped','hit wicket')
        GROUP BY bowler
        ORDER BY wickets DESC
        LIMIT {{ limit }};
    """),

    "team_wins": Template("""
        SELECT COUNT(*) AS wins
        FROM matches
        WHERE winner = '{{ team }}' AND season = {{ season }};
    """),

    "avg_score_venue": Template("""
        SELECT AVG(runs_per_match) AS avg_score
        FROM (
            SELECT match_id, SUM(total_runs) AS runs_per_match
            FROM deliveries
            JOIN matches ON deliveries.match_id = matches.id
            WHERE venue = '{{ venue }}'
            GROUP BY match_id
        ) AS scores;
    """)
}

def render_template(template_name, **kwargs):
    if template_name not in TEMPLATES:
        raise ValueError(f"Template '{template_name}' not found.")
    return TEMPLATES[template_name].render(**kwargs).strip()
