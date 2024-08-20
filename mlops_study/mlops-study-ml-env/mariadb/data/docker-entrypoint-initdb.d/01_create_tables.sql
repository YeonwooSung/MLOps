CREATE DATABASE IF NOT EXISTS mlops;

USE mlops;

DROP TABLE IF EXISTS `mlops`.`cust_info`;
CREATE TABLE `mlops`.`cust_info` (
  `base_dt` varchar(8) NOT NULL,
  `cust_id` varchar(10) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `married` varchar(5) DEFAULT NULL,
  `education` varchar(20) DEFAULT NULL,
  `self_employed` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`base_dt`,`cust_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY KEY(`base_dt`)
PARTITIONS 8
;

DROP TABLE IF EXISTS `mlops`.`family_info`;
CREATE TABLE `mlops`.`family_info` (
  `base_dt` varchar(8) NOT NULL,
  `cust_id` varchar(10) NOT NULL,
  `family_cust_id` varchar(10) NOT NULL,
  `living_together` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`base_dt`,`cust_id`,`family_cust_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY KEY(`base_dt`)
PARTITIONS 8
;

DROP TABLE IF EXISTS `mlops`.`loan_default_account`;
CREATE TABLE `mlops`.`loan_default_account` (
  `loan_account_id` varchar(12) NOT NULL,
  `registration_date` varchar(8) DEFAULT NULL,
  `registration_time` varchar(6) DEFAULT NULL,
  `loan_default` varchar(5) DEFAULT NULL,
  PRIMARY KEY (`loan_account_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

DROP TABLE IF EXISTS `mlops`.`loan_applicant_info`;
CREATE TABLE `mlops`.`loan_applicant_info` (
  `applicant_id` varchar(10) NOT NULL,
  `applicant_date` varchar(8) NOT NULL,
  `applicant_time` varchar(6) NOT NULL,
  `cust_id` varchar(10) NOT NULL,
  `applicant_income` bigint(20) DEFAULT NULL,
  `coapplicant_income` bigint(20) DEFAULT NULL,
  `credit_history` decimal(5,2) DEFAULT NULL,
  `property_area` varchar(10) DEFAULT NULL,
  `loan_amount` bigint(20) DEFAULT NULL,
  `loan_amount_term` int(11) DEFAULT NULL,
  `loan_account_id` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

DROP TABLE IF EXISTS `mlops`.`ineligible_loan_model_features`;
CREATE TABLE `mlops`.`ineligible_loan_model_features` (
  `base_dt` varchar(8) NOT NULL,
  `applicant_id` varchar(10) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `married` varchar(5) DEFAULT NULL,
  `family_dependents` varchar(21) DEFAULT NULL,
  `education` varchar(20) DEFAULT NULL,
  `self_employed` varchar(5) DEFAULT NULL,
  `applicant_income` bigint(20) DEFAULT NULL,
  `coapplicant_income` bigint(20) DEFAULT NULL,
  `loan_amount` bigint(20) DEFAULT NULL,
  `loan_amount_term` int(11) DEFAULT NULL,
  `credit_history` decimal(5,2) DEFAULT NULL,
  `property_area` varchar(10) DEFAULT NULL,
  PRIMARY KEY (`base_dt`, `applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

DROP TABLE IF EXISTS `mlops`.`ineligible_loan_model_result`;
CREATE TABLE `mlops`.`ineligible_loan_model_result` (
  `base_dt` varchar(8) NOT NULL,
  `applicant_id` varchar(10) NOT NULL,
  `predict` int(10) DEFAULT NULL,
  `probability` double DEFAULT NULL,
  PRIMARY KEY (`base_dt`, `applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

DROP TABLE IF EXISTS `mlops`.`ineligible_loan_model_features_target`;
CREATE TABLE `mlops`.`ineligible_loan_model_features_target` (
  `base_ym` varchar(8) NOT NULL,
  `applicant_id` varchar(10) NOT NULL,
  `gender` varchar(10) DEFAULT NULL,
  `married` varchar(5) DEFAULT NULL,
  `family_dependents` varchar(21) DEFAULT NULL,
  `education` varchar(20) DEFAULT NULL,
  `self_employed` varchar(5) DEFAULT NULL,
  `applicant_income` bigint(20) DEFAULT NULL,
  `coapplicant_income` bigint(20) DEFAULT NULL,
  `loan_amount_term` int(11) DEFAULT NULL,
  `credit_history` decimal(5,2) DEFAULT NULL,
  `property_area` varchar(10) DEFAULT NULL,
  `loan_status` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`base_ym`, `applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;


CREATE DATABASE IF NOT EXISTS mlops_meta;

USE mlops_meta;

DROP TABLE IF EXISTS `mlops_meta`.`model_api_log`;
CREATE TABLE `mlops_meta`.`model_api_log` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `model_name` varchar(50) NOT NULL,
  `model_version` varchar(10) NOT NULL,
  `log_type` varchar(10) NOT NULL,
  `request_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `payload` longtext DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

DROP TABLE IF EXISTS `mlops_meta`.`model_ct_log`;
CREATE TABLE `mlops_meta`.`model_ct_log` (
  `model_name` varchar(50) NOT NULL,
  `model_version` varchar(10) NOT NULL,
  `started_time` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `finished_time` TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  `metrics` longtext DEFAULT NULL,
  `training_cutoff_date` varchar(10) NOT NULL,
  PRIMARY KEY (`model_name`, `model_version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
;

create database if not exists recipe;

USE recipe;

DROP TABLE IF EXISTS `recipe`.`recipe_target_applicants`;
CREATE TABLE `recipe`.`recipe_target_applicants` (
  `base_dt` varchar(8) NOT NULL,
  `applicant_id` varchar(10) NOT NULL,
  `loan_account_id` varchar(12) DEFAULT NULL,
  PRIMARY KEY (`base_dt`, `applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY KEY(`base_dt`)
PARTITIONS 8
;

DROP TABLE IF EXISTS `recipe`.`recipe_target_applicants_new_id`;
CREATE TABLE `recipe`.`recipe_target_applicants_new_id` (
  `base_dt` varchar(8) NOT NULL,
  `applicant_id` varchar(10) NOT NULL,
  `new_applicant_id` varchar(34) DEFAULT NULL,
  `loan_account_id` varchar(12) DEFAULT NULL,
  `new_loan_account_id` varchar(36) DEFAULT NULL,
  PRIMARY KEY (`base_dt`, `applicant_id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4
PARTITION BY KEY(`base_dt`)
PARTITIONS 8
;
