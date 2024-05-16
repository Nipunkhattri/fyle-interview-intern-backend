SELECT teacher_id, COUNT(*) AS max_grade_a_value
FROM assignments
WHERE grade = 'A'
GROUP BY teacher_id
ORDER BY max_grade_a_value DESC
LIMIT 1;
