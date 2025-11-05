import os
import json
from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from pydantic import BaseModel, Field, validator
from typing import Optional
from database import execute_query
from prompts import (
    SYSTEM_PROMPT,
    DATABASE_SCHEMA,
    SQL_GENERATION_PROMPT,
    VEGA_GENERATION_PROMPT,
    ANALYSIS_PROMPT
)

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0, api_key=os.getenv('OPENAI_API_KEY'))

class UserQuery(BaseModel):
    message: str = Field(..., min_length=1, max_length=500, description="User query message")
    
    @validator('message')
    def validate_message(cls, v):
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()

class SQLResponse(BaseModel):
    sql_query: str = Field(..., description="Generated SQL query")
    
    @validator('sql_query')
    def validate_sql(cls, v):
        if not v.strip():
            raise ValueError("SQL query cannot be empty")
        
        v = v.strip()
        v = v.replace("```sql", "").replace("```", "").strip()
        
        if v.upper().startswith("SQL:"):
            v = v[4:].strip()
        
        if v.upper() == "INVALID_FIELD":
            raise ValueError("Query contains invalid or non-existent fields")
        
        forbidden_keywords = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', 'TRUNCATE']
        upper_sql = v.upper()
        for keyword in forbidden_keywords:
            if keyword in upper_sql:
                raise ValueError(f"Forbidden SQL operation: {keyword}")
        
        return v

def process_user_query(user_message):
    try:
        sql_query = generate_sql(user_message)

        if not sql_query:
            return {
                "text": "I couldn't understand your question. Could you rephrase it?",
                "vega_spec": None
            }
        print(sql_query)
        query_results = execute_query(sql_query)

        if not query_results:
            return {
                "text": "No data found for your query.",
                "vega_spec": None
            }

        vega_spec = generate_vega_spec(user_message, sql_query, query_results)
        analysis_text = generate_analysis(user_message, query_results)

        return {
            "text": analysis_text,
            "vega_spec": vega_spec
        }

    except ValueError as e:
        error_msg = str(e)
        if "invalid or non-existent fields" in error_msg.lower():
            return {
                "text": "Sorry, the fields you're asking about don't exist in our database. I can only query paper titles, years, research fields, citation counts, and author names and affiliations. Please rephrase your question.",
                "vega_spec": None
            }
        else:
            return {
                "text": "Sorry, there was an issue processing your query. Please rephrase your question.",
                "vega_spec": None
            }
    except Exception as e:
        return {
            "text": "Sorry, the system encountered a technical issue. Please try again later.",
            "vega_spec": None
        }

def generate_sql(user_message):
    try:
        user_query = UserQuery(message=user_message)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", SYSTEM_PROMPT),
            ("system", DATABASE_SCHEMA),
            ("system", SQL_GENERATION_PROMPT),
            ("user", "Generate SQL for: {user_message}")
        ])
        
        output_parser = StrOutputParser()
        chain = prompt | llm | output_parser
        
        raw_sql = chain.invoke({"user_message": user_query.message})
        
        sql_response = SQLResponse(sql_query=raw_sql)
        return sql_response.sql_query
        
    except ValueError as e:
        error_msg = str(e)
        if "invalid or non-existent fields" in error_msg.lower():
            raise ValueError("Query contains invalid or non-existent fields")
        else:
            raise ValueError(f"SQL generation failed: {error_msg}")
    except Exception as e:
        raise ValueError(f"SQL generation failed: {str(e)}")

def generate_vega_spec(user_message, sql_query, results):
    messages = [
        {"role": "system", "content": VEGA_GENERATION_PROMPT},
        {"role": "user", "content": f"User question: {user_message}\nSQL query: {sql_query}\nResults: {json.dumps(results)}\n\nGenerate a Vega-Lite spec for this data."}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0
    )

    vega_json = response.choices[0].message.content.strip()
    vega_json = vega_json.replace("```json", "").replace("```", "").strip()

    try:
        vega_spec = json.loads(vega_json)
        vega_spec["data"]["values"] = results
        return vega_spec
    except:
        return None

def generate_analysis(user_message, results):
    messages = [
        {"role": "system", "content": ANALYSIS_PROMPT},
        {"role": "user", "content": f"User question: {user_message}\nData: {json.dumps(results[:10])}\n\nProvide a brief analysis."}
    ]

    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=messages,
        temperature=0.7
    )

    return response.choices[0].message.content.strip()
