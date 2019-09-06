DELIMITER $$
CREATE DEFINER=`webdev`@`localhost` PROCEDURE `getAllProjects`()

BEGIN 
	SELECT title, body, start_date, end_date, short_description FROM project;
END$$
DELIMITER; 