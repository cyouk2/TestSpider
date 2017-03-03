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

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_lines` AS select `piainfototal`.`shop` AS `shop`,`piainfototal`.`taino` AS `taino`,count(0) AS `liness` from `piainfototal` group by `piainfototal`.`shop`,`piainfototal`.`taino` order by `liness` desc limit 500;

CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_rate_info` AS select `piainfototal`.`shop` AS `shop`,`piainfototal`.`taino` AS `taino`,`piainfototal`.`playdate` AS `playdate`,sum(`piainfototal`.`bonus`) AS `bonus`,sum(`piainfototal`.`starttotal`) AS `starts`,truncate(ifnull((sum(`piainfototal`.`starttotal`) / sum(`piainfototal`.`bonus`)),0),1) AS `rate` from `piainfototal` group by `piainfototal`.`shop`,`piainfototal`.`playdate`,`piainfototal`.`taino` order by `piainfototal`.`shop`,`piainfototal`.`taino`,`piainfototal`.`playdate`;

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

