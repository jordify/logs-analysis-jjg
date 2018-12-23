#!/usr/bin/env python3

# A reporting tool to help analyze our news articles

import psycopg2
from datetime import datetime

# Name of the database containing statistics on articles
DBNAME = 'news'


def most_popular_articles(n=0):
    '''Returns the articles accessed the most for all time

    n: number of articles to display (i.e. top n), n = 0 will print all
    articles in descending order'''
    # Connect to DB and pull all articles and view count (descending order)
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("select title, view_count from article_view_count")
    rows = c.fetchall()
    db.close()

    # Pretty print the number of articles requested
    if n == 0:
        n = len(rows)
    for row in rows[:n]:
        print("\"{:s}\" — {:d} views".format(row[0], row[1]))
    return True


def most_popular_authors(n=0):
    '''Returns the authors whose articles have been accessed the most

    n: number of authors to display (i.e. top n), n = 0 will print all authors
    in descending order'''
    # Connect to DB and pull authors with total view count (descending order)
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("select name, sum(view_count)::integer as total_views from\
        article_view_count group by name order by total_views desc")
    rows = c.fetchall()
    db.close()

    # Pretty print the number of authors requested
    if n == 0:
        n = len(rows)
    for row in rows[:n]:
        print("{:s} — {:d} views".format(row[0], row[1]))
    return True


def error_prone_days():
    '''Returns all days for which more than 1% of requests lead to errors'''
    # Connect to DB and pull days with error % greater than 1%
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    c.execute("select date, error_percentage from access_by_date where\
        error_percentage >= 0.01 order by date")
    rows = c.fetchall()
    db.close()

    # Pretty print the days above 1% error rate
    for row in rows:
        print("{:s} — {:.2%} views".format(row[0].strftime("%B %d, %Y"),
              row[1]))
    return True


if __name__ == '__main__':
    print("Log analysis starting:")
    print("1. What are the most popular three articles of all time?")
    most_popular_articles(3)
    print("\n2. Who are the most popular article authors of all time?")
    most_popular_authors()
    print("\n3. On which days did more than 1% of requests lead to errors?")
    error_prone_days()
