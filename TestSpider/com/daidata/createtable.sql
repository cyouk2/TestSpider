CREATE TABLE `piainfotoday` (
  `shop` varchar(45) NOT NULL,
  `playdate` varchar(45) NOT NULL,
  `taino` varchar(45) NOT NULL,
  `bonus` varchar(45) DEFAULT '0',
  `bonusforst` varchar(45) DEFAULT '0',
  `laststart` varchar(45) DEFAULT '0',
  `rate` varchar(45) DEFAULT '0',
  `allstart` varchar(45) DEFAULT '0',
  PRIMARY KEY (`shop`,`playdate`,`taino`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;
