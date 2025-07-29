from langchain.tools import tool
from analytics.comparisons     import compare_players
from analytics.metrics         import top_run_scorers, top_wicket_takers, average_match_score
from analytics.predictions     import predict_total_score
from analytics.summaries       import generate_match_summary
from analytics.team            import season_win_counts, powerplay_scores, win_percentage
from agents.langchain_sql_agent import ask_sql
from viz.charts                import bar_chart, line_chart
from matplotlib.figure         import Figure
from typing import List, Dict, Any, Union
import ast
import operator as op


@tool
def get_comparison(players: str) -> str:
    """Compare two players. Input: 'Player1 vs Player2'"""
    try:
        p1, p2 = [p.strip() for p in players.split("vs")]
        df = compare_players(p1, p2)
        return f"Final Answer:\n{df.to_string(index=False)}"
    except:
        return "Final Answer: Please format input like 'Player1 vs Player2'"


@tool
def get_top_scorers(season_and_limit: str) -> str:
    """Get top N run scorers. Input: '2015, 5'"""
    try:
        season, limit = [int(x.strip()) for x in season_and_limit.split(",")]
        df = top_run_scorers(season, limit)
        return f"Final Answer:\n{df.to_string(index=False)}"
    except:
        return "Final Answer: Please use format like '2016, 5'"


@tool
def get_top_wicket_takers(season: str) -> str:
    """Get top 5 wicket takers in a season. Input: '2014'"""
    try:
        df = top_wicket_takers(season=int(season), limit=5)
        return f"Final Answer:\n{df.to_string(index=False)}"
    except:
        return "Final Answer: Please provide a valid season."


@tool
def get_venue_avg(venue: str) -> str:
    """Get average match score at a venue/stadium. Input: 'Wankhede Stadium'"""
    try:
        df = average_match_score(venue)
        score = round(df.iloc[0, 0], 2)
        return f"Final Answer: Average score at {venue} is {score} runs."
    except:
        return "Final Answer: Please provide a valid venue name."


@tool
def get_team_wins(team: str) -> str:
    """Get number of wins per season. Input: 'Mumbai Indians'"""
    try:
        df = season_win_counts(team)
        return f"Final Answer:\n{df.to_string(index=False)}"
    except:
        return "Final Answer: Invalid team name."


@tool
def get_powerplay_runs(team_and_season: str) -> str:
    """Powerplay totals per match. Input: 'Mumbai Indians, 2015'"""
    try:
        team, season = [s.strip() for s in team_and_season.split(",")]
        df = powerplay_scores(team, int(season))
        return f"Final Answer:\n{df.to_string(index=False)}"
    except:
        return "Final Answer: Format should be 'Team Name, Year'"


@tool
def get_win_percent(team: str) -> str:
    """Overall win percentage of a team. Input: 'Chennai Super Kings'"""
    try:
        df = win_percentage(team)
        percent = df['win_percent'].iloc[0]
        return f"Final Answer: {team} win percentage is {percent}%"
    except:
        return "Final Answer: Invalid team name."


@tool
def get_score_prediction(dummy: str = "predict") -> str:
    """Predict 1st innings score using regression model."""
    try:
        mae, model, enc = predict_total_score()
        return f"Final Answer: Model MAE is {mae} runs. Use predict_for_input() for match-specific input."
    except:
        return "Final Answer: Prediction model failed."


@tool
def get_match_summary(match_id: str) -> str:
    """Summarize match by ID. Input: '392200'"""
    try:
        summary = generate_match_summary(int(match_id))
        return f"Final Answer:\n{summary}"
    except:
        return "Final Answer: Please provide a valid match ID."



@tool
def chart_player_comparison(players: str) -> List[Dict[str, Any]]:
    """
    Use this when the user requests a chart or plot comparison between two players.
    Returns a JSON-serializable list of dicts with keys: player, innings, total_runs,
    fours, sixes, balls_faced, strike_rate.
    """
    p1, p2 = [p.strip() for p in players.split("vs")]
    df = compare_players(p1, p2)
    return df.to_dict(orient="records")


@tool
def chart_team_wins(team: str) -> Figure:
    """Line chart of a team's wins per season."""
    df = season_win_counts(team)
    return line_chart(df, "season", "wins", title=f"{team} Wins Per Season")


@tool
def chart_powerplay_runs(team_and_season: str) -> Figure:
    """Chart powerplay scores per match."""
    team, season = [s.strip() for s in team_and_season.split(",")]
    df = powerplay_scores(team, int(season))
    return line_chart(df, "match_id", "powerplay_runs", title=f"{team} Powerplay Runs ({season})")


@tool
def sql_fallback(query: str) -> str:
    """Fallback to SQL for any query not handled by above tools."""
    res = ask_sql(query)
    df  = res["df"]
    if not df.empty:
        table = df.to_string(index=False)
        return f"Final Answer:\nSQL used:\n{res['sql']}\n\nResults:\n{table}"
    else:
        return "Final Answer: No results found for your query."

_OPERATORS = {
    ast.Add: op.add,
    ast.Sub: op.sub,
    ast.Mult: op.mul,
    ast.Div: op.truediv,
    ast.Pow: op.pow,
    ast.USub: op.neg,
}

def _eval_node(node: ast.AST) -> float:
    if isinstance(node, ast.Constant): 
        return float(node.value)
    if isinstance(node, ast.BinOp):
        left = _eval_node(node.left)
        right = _eval_node(node.right)
        oper = _OPERATORS[type(node.op)]
        return oper(left, right)
    if isinstance(node, ast.UnaryOp):
        operand = _eval_node(node.operand)
        oper = _OPERATORS[type(node.op)]
        return oper(operand)
    raise ValueError(f"Unsupported expression: {ast.dump(node)}")

@tool
def calculator(expression: str) -> Union[float, str]:
    """
    Perform a basic arithmetic calculation.
    Input: a string like "7 + (15 / 3) * 2"
    Supports +, -, *, /, **, and parentheses.
    Returns the numeric result or an error message.
    """
    try:
        expr_ast = ast.parse(expression, mode="eval").body
        result = _eval_node(expr_ast)
        return result
    except Exception as e:
        return f"Error evaluating expression: {e}"