from langchain.agents import initialize_agent, AgentType
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from langchain.schema import SystemMessage
import os

from agents.tool_registry import (
    get_comparison, get_top_scorers, get_top_wicket_takers,
    get_venue_avg, get_team_wins, get_powerplay_runs,
    get_win_percent, get_score_prediction, get_match_summary,
    chart_player_comparison, chart_team_wins, chart_powerplay_runs, sql_fallback, calculator
)

load_dotenv()

def get_multitool_agent():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    tools = [
        get_comparison, get_top_scorers, get_top_wicket_takers,
        get_venue_avg, get_team_wins, get_powerplay_runs,
        get_win_percent, get_score_prediction, get_match_summary,
        chart_player_comparison, chart_team_wins, chart_powerplay_runs, sql_fallback, calculator
    ]


    agent = initialize_agent(
            tools=tools,
            llm=llm,
            agent_type=AgentType.OPENAI_FUNCTIONS,
            verbose=True,
            return_direct=True,
            max_iterations=5,
            prefix_messages=[
                SystemMessage(
                    content=("You are a cricket-stats assistant that can both call tools "
                "and do simple arithmetic. If you retrieve two numbers "
                "(e.g. wins and total matches), you should compute percentages "
                "by dividing them yourself rather than stopping. "
                "Only call tools to *fetch* data; do basic math in your own reasoning."
            )
                )
            ],
            early_stopping_method="generate",
            handle_parsing_errors=True,
        )

    return agent
