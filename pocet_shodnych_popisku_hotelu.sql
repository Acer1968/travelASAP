SELECT SUM(count)
FROM (
    SELECT COUNT(*) as count
    FROM hotel_descriptions
    GROUP BY description
    HAVING COUNT(*) > 1
) as subquery;
