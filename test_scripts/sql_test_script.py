from router import route_question
from sql_agent import generate_sql
from sql_executor import execute_sql

question = input("Question: ")

decision = route_question(question)

if decision["route"] != "sql":
    print("This is not an SQL question.")
    exit()

sql = generate_sql(question)

print("\nGenerated SQL:\n")
print(sql)

df = execute_sql(sql)

print("\nReturned", len(df), "rows\n")

print(df.head())