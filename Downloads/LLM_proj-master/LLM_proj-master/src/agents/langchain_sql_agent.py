import os
import re
import pandas as pd
from dotenv import load_dotenv
from data.db_loader import connect_db

from langchain_community.utilities.sql_database import SQLDatabase
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.agents.agent_toolkits import create_sql_agent
from langchain.agents import AgentType

from agents.sql_prompt_template import get_sql_prompt_template

load_dotenv()

def clean_sql(output: str) -> str:
    """Clean SQL: remove markdown, fix spacing for Gemini-generated queries."""
    sql = re.sub(r"```sql|```", "", output).strip()

    sql = sql.replace("INNER JOIN", " INNER JOIN")
    sql = sql.replace("FROM", " FROM ")
    sql = sql.replace("WHERE", " WHERE ")
    sql = sql.replace("ON", " ON ")
    sql = sql.replace("\n", " ")
    sql = re.sub(r"\s+", " ", sql)
    return sql.strip()



def get_sql_agent():
    db = SQLDatabase.from_uri(
        "mysql+pymysql://root:" + os.getenv("MYSQL_PASSWORD") + "@localhost/cricstats"
    )

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-lite",
        temperature=0.2,
        google_api_key=os.getenv("GEMINI_API_KEY")
    )

    prompt = get_sql_prompt_template()

    agent = create_sql_agent(
        llm=llm,
        db=db,
        prompt=prompt,
        agent_type=AgentType.OPENAI_FUNCTIONS,
        verbose=True,
        return_direct=True,
        max_iterations=5,
        early_stopping_method="generate",
        
    )

    return agent

def ask_sql(question: str) -> dict:
    agent = get_sql_agent()

    result = agent.invoke({"input": question})
    sql_raw = result["output"] if isinstance(result, dict) else result
    sql_cleaned = clean_sql(sql_raw)

    try:
        df = pd.read_sql(sql_cleaned, connect_db())
    except Exception as e:
        df = pd.DataFrame()
        print(f"SQL Execution Error:\n{e}")

    return {
        "question": question,
        "sql": sql_cleaned,
        "df": df
    }
