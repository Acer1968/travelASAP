SELECT description,
       COUNT(*) as count,
       GROUP_CONCAT(Hotel_ID) as hotel_ids,
       GROUP_CONCAT(source) as sources,
       GROUP_CONCAT(description_type) as description_types
FROM hotel_descriptions
GROUP BY description
HAVING COUNT(*) > 1;

