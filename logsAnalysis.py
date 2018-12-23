#!/usr/bin/env python3

# A reporting tool to help analyze our news articles

import psycopg2
import argparse
from datetime import datetime

# Name of the database containing statistics on articles
DBNAME = 'news'

# SQL for creating the required additional views in the database
ARTICLE_VIEW_COUNT_SQL = '''\
CREATE VIEW article_view_count AS
    SELECT articles.title, authors.name, count(log.path) AS view_count
    FROM articles, log, authors
    WHERE log.path = '/article/' || articles.slug
        AND authors.id = articles.author
        AND log.status = '200 OK'
    GROUP BY articles.title, authors.name, log.path
    ORDER BY view_count DESC\
'''

ACCESS_BY_DATE_SQL = '''\
CREATE VIEW access_by_date AS
    WITH bad_access AS (
        SELECT DATE(time) AS date, COUNT(path) AS bad
        FROM log WHERE NOT (status = '200 OK')
        GROUP BY DATE(time)
        )
    SELECT DATE(time), COUNT(path) AS access_count,
        (bad/count(path)::FLOAT) AS error_percentage
    FROM log, bad_access
    WHERE DATE(time) = date
    GROUP BY DATE(time), bad
    ORDER BY date ASC\
'''


def most_popular_articles(n=0):
    '''Returns the articles accessed the most for all time

    n: number of articles to display (i.e. top n), n = 0 will print all
    articles in descending order'''
    # Connect to DB and pull all articles and view count (descending order)
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    try:
        c.execute("select title, view_count from article_view_count")
    except psycopg2.ProgrammingError as err:
        print("SQL ERROR: {:s}".format(err))
        raise
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
    try:
        c.execute("select name, sum(view_count)::integer as total_views from\
 article_view_count group by name order by total_views desc")
    except psycopg2.ProgrammingError as err:
        print("SQL ERROR: {:s}".format(err))
        raise
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
    try:
        c.execute("select date, error_percentage from access_by_date where\
            error_percentage >= 0.01 order by date")
    except psycopg2.ProgrammingError as err:
        print("SQL ERROR: {:s}".format(err))
        raise
    rows = c.fetchall()
    db.close()

    # Pretty print the days above 1% error rate
    for row in rows:
        print("{:s} — {:.2%} views".format(row[0].strftime("%B %d, %Y"),
              row[1]))
    return True


def create_views_in_db():
    '''Drops and recreates the views required by the SQL queries above'''
    db = psycopg2.connect(database=DBNAME)
    c = db.cursor()
    try:
        c.execute("drop view article_view_count")
        c.execute("drop view access_by_date")
    except psycopg2.ProgrammingError:
        db.rollback()
    c.execute(ARTICLE_VIEW_COUNT_SQL)
    c.execute(ACCESS_BY_DATE_SQL)
    db.commit()
    db.close()


def set_up_args(parser):
    '''Sets up command line argument parsing'''
    parser.add_argument("-c", "--create_views",
                        help="Recreate the views in the news database required for this\
 analysis and then run analysis",
                        action="store_true")
    return parser.parse_args()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    args = set_up_args(parser)
    if args.create_views:
        create_views_in_db()
    try:
        print("\033[1mLog analysis starting:")
        print("1. What are the most popular three articles of all\
 time?\033[0m")
        most_popular_articles(3)
        print("\n\033[1m2. Who are the most popular article authors of all\
 time?\033[0m")
        most_popular_authors()
        print("\n\033[1m3. On which days did more than 1% of requests lead to\
 errors?\033[0m")
        error_prone_days()
    except:
        print("\n\033[1mAnalysis Failed!\033[0m\nDid you create the initial\
 views using --create_views?")
