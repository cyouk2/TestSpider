DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `pro_prepare_data_c`()
BEGIN

	DECLARE done INT DEFAULT FALSE;
    DECLARE strShop varchar(45) DEFAULT '';
    DECLARE strTaino varchar(45) DEFAULT '';

    begin
    	declare mycur cursor for 
			SELECT shop, taino FROM v_lines;
        
		DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
		open mycur;
		read_loop: LOOP
			FETCH mycur INTO strShop,strTaino;
				call pro_prepare_data_b(strShop,strTaino);
			IF done THEN
				LEAVE read_loop;
			END IF;
		END LOOP;
		CLOSE mycur;
	end;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `pro_prepare_data_b`(IN shopid INT,IN tainoid INT)
BEGIN

	DECLARE done INT DEFAULT FALSE;
	DECLARE limiter INT DEFAULT 0;
    DECLARE strPlayDate varchar(45) DEFAULT '';

    begin
    	declare mycur cursor for 
			SELECT distinct playdate FROM beidou.piainfototal
			where shop=shopid and taino=tainoid;
        
		DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
		open mycur;
		read_loop: LOOP
			FETCH mycur INTO strPlayDate;
            	begin
					SELECT 
						COUNT(*)
					INTO limiter FROM beidou.piainfototal
					WHERE shop = shopid AND taino = tainoid AND playdate < strPlayDate;
					IF limiter < 31 THEN
                    ITERATE read_loop;
                    END IF;
				end;
				call pro_prepare_data(shopid,tainoid,strPlayDate);
			IF done THEN
				LEAVE read_loop;
			END IF;
		END LOOP;
		CLOSE mycur;
	end;
END$$
DELIMITER ;

DELIMITER $$
CREATE DEFINER=`root`@`localhost` PROCEDURE `pro_prepare_data`(IN shopid INT,IN tainoid INT,IN strPlayDate varchar(45))
BEGIN

	DECLARE done INT DEFAULT FALSE;
	DECLARE v_ballin varchar(45) DEFAULT '';
    DECLARE v_bonus varchar(45) DEFAULT '';
	DECLARE limiter INT DEFAULT 0;
	DECLARE offsetter INT DEFAULT 0;
    DECLARE X varchar(45) DEFAULT '';
    DECLARE XXX varchar(5000) DEFAULT '';
    DECLARE intRate INT DEFAULT 0;
    DECLARE intBonus INT DEFAULT 0;
	begin
		SELECT 
			COUNT(*)
		INTO limiter FROM
			beidou.piainfototal
		WHERE
			shop = shopid AND taino = tainoid
				AND playdate < strPlayDate;
		SELECT limiter - 30 INTO offsetter;
	end;
    begin
    	declare mycur cursor for 
			SELECT concat(ballin,concat(',',bonus)) as x FROM beidou.piainfototal
			where shop=shopid and taino=tainoid and playdate < strPlayDate
			order by playdate, convert(lineno,unsigned)
			limit limiter offset offsetter;
        
		DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;
		open mycur;
		read_loop: LOOP
			FETCH mycur INTO X;
			IF done THEN
				LEAVE read_loop;
			END IF;
			SELECT CONCAT(XXX, CONCAT(',', X)) INTO XXX;
		END LOOP;
		CLOSE mycur;
        
	end;
    begin
		SELECT (rate div 1 ), bonus  into intRate,intBonus
	    FROM v_rate_info
		WHERE shop = shopid AND taino = tainoid AND playdate = strPlayDate;
		INSERT INTO traindata(datas, rate, bonuslv,playdate, taino, shop)values(SUBSTRING(XXX,2),intRate,intBonus,strPlayDate,tainoid,shopid);
    end;
END$$
DELIMITER ;

SELECT `v_rate_info`.`shop`,
    `v_rate_info`.`taino`,
    `v_rate_info`.`playdate`,
    `v_rate_info`.`bonus`,
    `v_rate_info`.`starts`,
    `v_rate_info`.`rate`
FROM `beidou`.`v_rate_info`;

SELECT `v_lines`.`shop`,
    `v_lines`.`taino`,
    `v_lines`.`liness`
FROM `beidou`.`v_lines`;

CREATE TABLE `traindata` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `datas` varchar(5000) DEFAULT NULL,
  `rate` varchar(4) DEFAULT NULL,
  `bonuslv` varchar(45) DEFAULT NULL,
  `playdate` varchar(45) DEFAULT NULL,
  `taino` varchar(45) DEFAULT NULL,
  `shop` varchar(45) DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=1270 DEFAULT CHARSET=utf8;
