------------------------------------------------------TABLES------------------------------------------------------------
USE comic2;

CREATE TABLE user_role (
    role_id INT auto_increment NOT NULL,
    role_name VARCHAR(100) NOT NULL,
    PRIMARY KEY (role_id)
);
CREATE TABLE user_info (
    user_id INT auto_increment NOT NULL,
    user_first_name VARCHAR(100) NOT NULL,
	user_last_name VARCHAR(100) NOT NULL,
	user_phone_number VARCHAR(100) NOT NULL,
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
	role_id INT, 
    PRIMARY KEY (user_id),
	FOREIGN KEY (role_id) REFERENCES user_role (role_id)
);
CREATE TABLE raw_table (
    image_id INT auto_increment NOT NULL,
    image_date date NOT NULL,
    image BLOB,
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (image_id)
);
CREATE TABLE split_images (
    img_no INT NOT NULL,
    image_id INT NOT NULL,
    image BLOB,
	creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (img_no),
	FOREIGN KEY (image_id) REFERENCES raw_table (image_id)
);
CREATE TABLE comic_split_image_caption (
    Caption_id INT auto_increment NOT NULL,
    split_id INT,
    Caption_Text1 VARCHAR(1000) NOT NULL,
    Caption_Text2 VARCHAR(1000) NOT NULL,
	Caption_Text3 VARCHAR(1000) NOT NULL,
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (Caption_id),
	FOREIGN KEY (split_id) REFERENCES split_images (img_no)
);
CREATE TABLE split_image_object (
    Image_Object_id INT auto_increment NOT NULL,
    Image_object_name VARCHAR(100) NOT NULL,
    Object_text VARCHAR(100) NOT NULL,
    Split_id INT NOT NULL,
	creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (Image_Object_id),
    FOREIGN KEY (Split_id) REFERENCES split_images (img_no)
);
CREATE TABLE split_image_text (
    image_text_id INT auto_increment NOT NULL,
    split_id INT NOT NULL,
    Image_Text_split VARCHAR(1000) NOT NULL,
    Split_Image_Text_Audio BLOB,
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (image_text_id),
    FOREIGN KEY (split_id) REFERENCES split_images(img_no) 
);
Create table Chapter_comments (
	Comment_id int PRIMARY KEY not null auto_increment,
	User_id int,
	Chapter_id int,
	user_comment varchar(200),
	comment_date date not null,
	creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
foreign key(user_id) references	user_info(user_id),
foreign key(chapter_id) references	raw_table(image_id)
);
CREATE TABLE chapter_comments_into_text (
	comment_text_id int PRIMARY KEY not null auto_increment,
	Comment_id int,
    text_file VARCHAR(1000), 
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
	FOREIGN KEY (Comment_id) REFERENCES chapter_comments(Comment_id)
);
CREATE TABLE split_image_bubble_text (
    bubble_id INT auto_increment NOT NULL,
    bubble_name VARCHAR(100) NOT NULL,
    split_id INT NOT NULL,
	Bubble_Text VARCHAR(1000),
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100),
    updation_date date,
    PRIMARY KEY (bubble_id),
	FOREIGN KEY (split_id) REFERENCES split_images(img_no) 
);
CREATE TABLE split_image_bubble_text_merge (
    split_bubble_id INT auto_increment NOT NULL,
    spli_bubble_text VARCHAR(1000) NOT NULL,
    bubble_id INT NOT NULL,
    split_id INT NOT NULL,
    creation_date date,
    created_by varchar(100) ,
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (split_bubble_id),
    FOREIGN KEY (split_id) REFERENCES split_images(img_no),
	FOREIGN KEY (bubble_id) REFERENCES split_image_bubble_text(bubble_id)
);
CREATE TABLE final_text_to_voice (
    Voice_id INT auto_increment NOT NULL,
    split_id INT NOT NULL,
	voice_file BLOB,
    creation_date date,
    created_by varchar(100),
    updated_by varchar(100) ,
    updation_date date,
    PRIMARY KEY (Voice_id),
	FOREIGN KEY (split_id) REFERENCES split_images(img_no)
);
--------------------------------------------------View--------------------------------------------
CREATE 
    ALGORITHM = UNDEFINED 
    DEFINER = `root`@`localhost` 
    SQL SECURITY DEFINER
VIEW `comic`.`user_comments` AS
    SELECT 
        `comic`.`user_info`.`User_id` AS `user_id`,
        `comic`.`user_info`.`user_first_name` AS `user_first_name`,
        `comic`.`user_info`.`user_last_name` AS `user_last_name`,
        `comic`.`chapter_comments`.`Chapter_id` AS `chapter_id`,
        `comic`.`chapter_comments`.`user_comment` AS `user_comment`,
        `comic`.`chapter_comments`.`ratings` AS `ratings`
    FROM
        (`comic`.`user_info`
        JOIN `comic`.`chapter_comments` ON ((`comic`.`user_info`.`User_id` = `comic`.`chapter_comments`.`User_id`)))
    WHERE
        (`comic`.`chapter_comments`.`Chapter_id` = 7)

-----------------------------------------------Procedures-----------------------------------------
CREATE DEFINER=`root`@`localhost` PROCEDURE `GetComicReview`(IN s_comment_id INT)
BEGIN
	DECLARE review VARCHAR(100);
    select rating_review(ratings) into review FROM chapter_comments
    where comment_id = s_comment_id;
    if(review = 'Very Good') THEN
		SELECT 'This is a very good comic till date' as "Feedback";
        ELSEIF (review = 'GOOD') THEN
		SELECT 'This is a Good comic' as "Feedback";
        ELSEIF (review = 'Satisfactory') THEN
		SELECT 'This is an average comic' as "Feedback";
        ELSEIF (review = 'Not Satisfactory') THEN
		SELECT 'This comic is not satisfactory as per the user' as "Feedback";
        ELSEIF (review = 'Bad') THEN
		SELECT 'This is a very Bad comic' as "Feedback";
	END IF;
END


CREATE DEFINER=`root`@`localhost` PROCEDURE `GetRoleName`(IN rolename varchar(30))
BEGIN
    DECLARE username varchar(30);
    SELECT concat(user_info.user_first_name,' ', user_info.user_last_name) into @username from user_info, user_role
    WHERE 
		user_role.role_id = check_role(rolename)
        and user_info.role_id = user_role.role_id
        LIMIT 1;
END


CREATE DEFINER=`root`@`localhost` PROCEDURE `sum_of_two`(IN num1 INT,IN num2 INT,OUT sot INT)
BEGIN
    SET sot := num1 + num2;
END


--------------------------------------------Function---------------------------------------------
CREATE DEFINER=`root`@`localhost` FUNCTION `Check_role`(role_name varchar(100)) RETURNS int
    DETERMINISTIC
BEGIN
    DECLARE role_id INT;
    IF (role_name = 'Tester') THEN
        SET role_id = 101;
    ELSEIF (role_name = 'Developer') THEN
        SET role_id = 102;
    ELSEIF (role_name = 'Admin') THEN
        SET role_id = 103;
    END IF;
    RETURN role_id;
END


CREATE DEFINER=`root`@`localhost` FUNCTION `no_of_years`(date1 date) RETURNS int
    DETERMINISTIC
BEGIN
 DECLARE date2 DATE;
  Select current_date() into date2;
  RETURN day(date2)-day(date1);
END



CREATE DEFINER=`root`@`localhost` FUNCTION `rating_review`(rating int) RETURNS varchar(100) CHARSET utf8mb4
    DETERMINISTIC
BEGIN
	DECLARE hi varchar(100);
  if(rating = 1) THEN
	SET hi = 'Very Good';
	ELSEIF (rating = 2) THEN
		SET hi = 'GOOD';
	ELSEIF (rating = 3) THEN
		SET hi = 'Satisfactory';
    ELSEIF (rating = 4) THEN
		SET hi = 'Not Satisfactory';
    ELSE 
		SET hi = 'Bad';
	END IF;
  RETURN hi;
END

-----------------------------------------Subqueries------------------------------------------------
select user_comment from chapter_comments
where user_id in (select user_id from user_info where user_first_name = 'John');


SELECT u.user_first_Name, u.user_last_name, c.ratings = (SELECT COUNT(ratings) FROM chapter_comments WHERE chapter_id = 7 limit 1)
  FROM user_info u, chapter_comments c

----------------------------------------------Triggers and Privileges--------------------------------
Privileges
--------------------------------------------------------------------------------
CREATE USER 'saikumar'@'localhost'
  IDENTIFIED BY 'password';
GRANT ALL ON comic.* TO 'saikumar'@'localhost';
flush privileges;

CREATE USER 'uday'@'localhost'
  IDENTIFIED BY 'password';
GRANT ALL ON comic.* TO 'uday'@'localhost';
flush privileges;

CREATE USER 'sathwik'@'localhost'
  IDENTIFIED BY 'password';
GRANT SELECT ON comic.users TO 'sathwik'@'localhost';
flush privileges;

---------------------------------------------------------------------------------
Triggers-  show triggers
---------------------------------------------------------------------------------
DELIMITER ;;
CREATE TRIGGER `creation_date_users` BEFORE INSERT ON `users` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;
-------------
DELIMITER ;;
CREATE TRIGGER `creation_date_raw_table` BEFORE INSERT ON `raw_table` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_user_info` BEFORE INSERT ON `user_info` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_split_images` BEFORE INSERT ON `split_images` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_chapter_comments` BEFORE INSERT ON `chapter_comments` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

-------------------

DELIMITER ;;
CREATE TRIGGER `creation_date_user_role` BEFORE INSERT ON `user_role` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_comic_strip_Image` BEFORE INSERT ON `comic_strip_Image` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_comic_strip_split_image` BEFORE INSERT ON `comic_strip_split_image` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_comic_split_image_caption` BEFORE INSERT ON `comic_split_image_caption` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_split_image_object` BEFORE INSERT ON `split_image_object` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_split_image_text` BEFORE INSERT ON `split_image_text` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_strip_chapter_comments` BEFORE INSERT ON `strip_chapter_comments` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_chapter_comments_into_text` BEFORE INSERT ON `chapter_comments_into_text` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_split_image_bubble_text` BEFORE INSERT ON `split_image_bubble_text` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_split_image_bubble_text_merge` BEFORE INSERT ON `split_image_bubble_text_merge` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;

DELIMITER ;;
CREATE TRIGGER `creation_date_final_text_to_voice` BEFORE INSERT ON `final_text_to_voice` FOR EACH ROW
BEGIN
    SET NEW.creation_date = NOW();
	SET NEW.created_by = user();
END;;
DELIMITER ;



