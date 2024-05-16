SELECT student_id, COUNT(*) AS graded_assignment_count
FROM assignments
WHERE state = 'GRADED'
GROUP BY student_id;
