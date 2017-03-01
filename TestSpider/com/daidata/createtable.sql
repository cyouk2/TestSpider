CREATE ALGORITHM=UNDEFINED DEFINER=`root`@`localhost` SQL SECURITY DEFINER VIEW `v_days` AS 
SELECT shop,playdate,taino,sum(bonus) as b,sum(ballin) as bin, TRUNCATE(IFNULL(sum(ballin)/sum(bonus),0),1) as rate
FROM beidou.piainfototal
group by shop,playdate,taino;

update piainfototal
set starttotal = ballin
where bonus = 0 and lineno > 0;
