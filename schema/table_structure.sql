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
  `pay_mode` varchar(20) NOT NULL DEFAULT 'cheque',
  `account_no` int(30),
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
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

CREATE TABLE IF NOT EXISTS `salary_structure` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL,
  `basic` int(15) NOT NULL DEFAULT 0.0,
  `HRA` int(15) NOT NULL DEFAULT 0.0,
  `conveyence` int(15) NOT NULL DEFAULT 0.0,
  `medical` int(15) NOT NULL DEFAULT 0.0,
  `pt` int(15) NOT NULL DEFAULT 0.0,
  `tds` int(15) NOT NULL DEFAULT 0.0,
  `monthly_leaves` int(5) NOT NULL DEFAULT 0,
  `vacation_leaves` int(5) NOT NULL DEFAULT 0,
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `expenses` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(20) NOT NULL, 
  `basic` int(20) NOT NULL,
  `HRA` int(20) NOT NULL,
  `conveyence` into(20) NOT NULL,
);

