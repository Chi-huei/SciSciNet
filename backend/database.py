import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def get_connection():
    database_url = os.getenv('DATABASE_URL')
    conn = psycopg2.connect(database_url)
    return conn

def execute_query(sql):
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(sql)
        columns = [desc[0] for desc in cursor.description]
        results = cursor.fetchall()

        data = []
        for row in results:
            row_dict = {}
            for i, col in enumerate(columns):
                row_dict[col] = row[i]
            data.append(row_dict)

        cursor.close()
        conn.close()
        return data
    except Exception as e:
        cursor.close()
        conn.close()
        raise e

def get_database_schema():
    schema_info = {
        "papers": {
            "columns": ["id", "title", "year", "field", "citation_count"],
            "description": "Contains paper information including id, title, publication year, research field, and citation count"
        },
        "authors": {
            "columns": ["id", "name", "affiliation"],
            "description": "Contains author information including id, name, and affiliation"
        },
        "author_paper": {
            "columns": ["author_id", "paper_id"],
            "description": "Junction table linking authors to papers"
        }
    }
    return schema_info
