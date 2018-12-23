#!/usr/bin/env python3
# 
# A reporting tool to help analyze our news articles

import psycopg2

# Name of the database containing statistics on articles
DBNAME = 'news'

def most_popular_articles(n = 10):
  '''Returns the articles accessed the most for all time'''
  return ''

def most_popular_authors(n = 10):
  '''Returns the authors whose articles have been accessed the most'''
  return ''

def error_prone_days():
  '''Returns all days for which more than 1% of requests lead to errors'''
  return ''

if __name__ == '__main__':
