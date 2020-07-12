import psycopg2
import os
try:
    # db_secret = os.environ["DATABASE_URL"]
    db_secret = 'postgres://gzgzsoahxgsnew:8415a9641dfe0f6d1ed4d9f2f8aca92b960eb9f357633e9a0677343c44d87fe4@ec2-52-200-48-116.compute-1.amazonaws.com:5432/d58urfihu94ic7'
    connection = psycopg2.connect(db_secret)
    connection.set_session(autocommit=True)

    cur = connection.cursor()
    cur.execute("""
    SELECT table_name
    FROM information_schema.tables
    WHERE table_schema='public'
    AND table_type='BASE TABLE';
    """)
    rows = cur.fetchall()
    print('Table list:')
    for row in rows:
        print("   ", row[0])
    cur.close()

except (Exception, psycopg2.Error) as error :
    print ("Error while connecting to PostgreSQL", error)

def get_student_data():
    cur = connection.cursor()
    cur.execute("""
    SELECT first_name, last_name, age 
    FROM student;
    """)
    rows = cur.fetchall()
    print('Student firstname:')
    print(rows)
    cur.close()
    return rows

get_student_data()