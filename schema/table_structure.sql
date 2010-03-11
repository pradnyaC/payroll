SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `payroll`
--

-- --------------------------------------------------------

--
-- Table structure for table `users`
--

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `name` varchar(255) NOT NULL, 
  `DOB` timestamp NOT NULL default '0000-00-00 00:00:00',
  `mobile` int(10) NOT NULL, 
  `permanant_address` varchar(255) NOT NULL, 
  `communication_address` varchar(255) NOT NULL, 
  `designation` varchar(255) NOT NULL,
  `team` varchar(255) NOT NULL,
  `joined_on` timestamp NOT NULL default '0000-00-00 00:00:00',
  `pan` int(10) NOT NULL DEFAULT 0,
  `salary_mode` varchar(20) NOT NULL DEFAULT 'cheque',
  `account_no` int(30) NOT NULL DEFAULT 0,
  `vacation_leaves` int(5) NOT NULL DEFAULT 0,
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `user_struct` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  `desc` varchar(255),
  `obj_type` varchar(255) NOT NULL DEFAULT 'char',
  `required` INT(1) NOT NULL DEFAULT 0
);

INSERT INTO user_struct (`name`, `desc`, `required`) VALUES ('ename', 'Employee Name', 1);
INSERT INTO user_struct (`name`, `desc`,`obj_type`, `required`) VALUES ('DOB', 'Date of Birth', 'date', 1);
INSERT INTO user_struct (`name`, `desc`,`obj_type`) VALUES ('mobile', 'Mobile Number', 'int');
INSERT INTO user_struct (`name`, `desc`) VALUES ('permanant_address', 'permanant_address');
INSERT INTO user_struct (`name`, `desc`, `required`) VALUES ('communication_address', 'communication_address', 1);
INSERT INTO user_struct (`name`, `desc`) VALUES ('designation', 'designation');
INSERT INTO user_struct (`name`, `desc`) VALUES ('team', 'team');
INSERT INTO user_struct (`name`, `desc`,`obj_type`) VALUES ('joined_on', 'joined_on', 'date');
INSERT INTO user_struct (`name`, `desc`,`obj_type`) VALUES ('pan', 'pan', 'int');
INSERT INTO user_struct (`name`, `desc`) VALUES ('salary_mode', 'salary_mode');
INSERT INTO user_struct (`name`, `desc`,`obj_type`) VALUES ('account_no', 'account_no', 'int');
INSERT INTO user_struct (`name`, `desc`) VALUES ('vacation_leaves', 'vacation_leaves', 'int');

CREATE TABLE IF NOT EXISTS `salary_struct` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `name` varchar(255) NOT NULL,
  `desc` varchar(255),
  `value` int(20) NOT NULL DEFAULT 0.0,
  `obj_type` varchar(255) NOT NULL DEFAULT 'int',
  `required` INT(1) NOT NULL DEFAULT 0
);

INSERT INTO `salary_struct` (`name`, `desc`, `value`, `required`) VALUES ('basic', 'Basic Salary', '0', 1);
INSERT INTO `salary_struct` (`name`, `desc`, `value`) VALUES ('HRA', 'HRA', '10000');
INSERT INTO `salary_struct` (`name`, `desc`, `value`) VALUES ('conveyence', 'conveyence', '500');
INSERT INTO `salary_struct` (`name`, `desc`, `value`) VALUES ('medical', 'medical', '1200');
INSERT INTO `salary_struct` (`name`, `desc`, `value`) VALUES ('pt', 'professional tax', '-12.5%');
INSERT INTO `salary_struct` (`name`, `desc`, `value`) VALUES ('tds', 'TDS', '-10%');


CREATE TABLE IF NOT EXISTS `salary` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL,
  `basic` int(15) NOT NULL DEFAULT 0.0,
  `HRA` int(15) NOT NULL DEFAULT 0.0,
  `conveyence` int(15) NOT NULL DEFAULT 0.0,
  `medical` int(15) NOT NULL DEFAULT 0.0,
  `pt` int(15) NOT NULL DEFAULT 0.0,
  `tds` int(15) NOT NULL DEFAULT 0.0,
  `deleted` tinyint(4) DEFAULT '0',
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
);



CREATE TABLE IF NOT EXISTS `master_data` (
  `HRA` int(15) NOT NULL DEFAULT 0.0,
  `conveyence` int(15) NOT NULL DEFAULT 0.0,
  `medical` int(15) NOT NULL DEFAULT 0.0,
  `PT` int(15) NOT NULL DEFAULT 0.0,
  `TDS` int(15) NOT NULL DEFAULT 0.0
  `monthly_leaves` int(5) NOT NULL DEFAULT 0,
  `vacation_leaves` int(5) NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS `leaves` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL,
  `leave_on` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00',
  `leave_type` varchar(20) NOT NULL DEFAULT 'month',
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `users_history` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL, 
  `designation` varchar(255) NOT NULL,
  `team` varchar(255) NOT NULL,
  `deleted` tinyint(4) default '0',
  `from_date` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `to_date` timestamp NOT NULL default '0000-00-00 00:00:00',
);

CREATE TABLE IF NOT EXISTS `increments` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL, 
  `amount` int(20) NOT NULL,
  `on_component` varchar(255) NOT NULL,
  `increment_on` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
);

CREATE TABLE IF NOT EXISTS `expenses` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL, 
  `basic` int(20) NOT NULL,
  `HRA` int(20) NOT NULL,
  `conveyence` into(20) NOT NULL,
);

