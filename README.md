# Logs Analysis

A reporting tool to help analyze our news articles

## How to Use It

Lorem ipsum

## Views Set Up in the Database

Two views have been added to the database schema to assist in analysis. These view can 
be created by running the following:

### New View: article_view_count
This view gives the count of successful GET requests for each article and includes the author's name:
```sql
CREATE VIEW article_view_count AS
  SELECT articles.title, authors.name, count(log.path) AS view_count
  FROM articles, log, authors
  WHERE log.path = '/article/' || articles.slug
    AND authors.id = articles.author
    AND log.status = '200 OK'
  GROUP BY articles.title, authors.name, log.path
  ORDER BY view_count DESC;
```

### New View: access_by_day
This view gives the count of hits to the site by day and what percentage of those resulted in an `404 NOT FOUND` error
```sql
CREATE VIEW access_by_date AS
  WITH bad_access AS
    (SELECT DATE(time) AS date, COUNT(path) AS bad
      FROM log WHERE NOT (status = '200 OK')
      GROUP BY DATE(time)
    )
  SELECT DATE(time), COUNT(path) AS access_count, (bad/count(path)::FLOAT) AS error_percentage
    FROM log, bad_access
    WHERE DATE(time) = date
    GROUP BY DATE(time), bad
    ORDER BY date ASC;
```

## Contributing

Lorem ipsum

## License

The contents of this repository are covered under the [MIT License](LICENSE).
