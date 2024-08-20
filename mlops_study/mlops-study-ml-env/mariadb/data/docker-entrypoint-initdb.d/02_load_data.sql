LOAD DATA INFILE '/tmp/mlops.cust_info.csv'
INTO TABLE `mlops`.`cust_info`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/tmp/mlops.family_info.csv'
INTO TABLE `mlops`.`family_info`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/tmp/mlops.loan_default_account.csv'
INTO TABLE `mlops`.`loan_default_account`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;

LOAD DATA INFILE '/tmp/mlops.loan_applicant_info.csv'
INTO TABLE `mlops`.`loan_applicant_info`
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 ROWS;
