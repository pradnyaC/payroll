
CREATE TABLE employee (empid int(20) NOT NULL auto_increment PRIMARY KEY, details longblob);
CREATE TABLE users (userid varchar(255), name varchar(255), email varchar(255));
CREATE TABLE salary (empid varchar(255), details longblob);
CREATE TABLE leaves (leave_key varchar(255), details longblob);
CREATE TABLE expenses (expenseid varchar(255), details longblob);
CREATE TABLE holidays (holiday timestamp NOT NULL, reason varchar(255));
CREATE TABLE working_sat (satid varchar(255), details longblob);

CREATE TABLE vacation_leave_accnt (empid int(20) NOT NULL, leaves int(20));



SET SQL_MODE="NO_AUTO_VALUE_ON_ZERO";

--
-- Database: `payroll`
--

-- --------------------------------------------------------
--
-- Table structure for table `types of objects in database`
--

CREATE TABLE IF NOT EXISTS `types_master` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `col_type` varchar(255) NOT NULL,
  `mysql_type` varchar(255) NOT NULL
);

INSERT INTO `types_master` (`col_type`, `mysql_type`) VALUES ('int', 'integer');
INSERT INTO `types_master` (`col_type`, `mysql_type`) VALUES ('string', 'varchar(255)');
INSERT INTO `types_master` (`col_type`, `mysql_type`) VALUES ('date', 'timestamp');
INSERT INTO `types_master` (`col_type`, `mysql_type`) VALUES ('percent', 'integer');

--------------------------------------------------------------------------------------------
--
-- Table structure for table `employee`
--

CREATE TABLE IF NOT EXISTS `employee_struct_cat` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `cat` varchar(50) NOT NULL
);

INSERT INTO `employee_struct_cat` (`cat`) VALUES ('Personal');
INSERT INTO `employee_struct_cat` (`cat`) VALUES ('Professional');
INSERT INTO `employee_struct_cat` (`cat`) VALUES ('Emergency Concact');
INSERT INTO `employee_struct_cat` (`cat`) VALUES ('Leaves');
INSERT INTO `employee_struct_cat` (`cat`) VALUES ('Salary');

CREATE TABLE IF NOT EXISTS `employee_struct` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `col_name` varchar(20) NOT NULL,
  `col_desc` varchar(255) NOT NULL,
  `col_type` varchar(10) NOT NULL REFERENCES `type_master`,
  `max_lenght` integer DEFAULT 0,
  `required` TINYINT NOT NULL DEFAULT 0,
  `category` varchar(20) REFERENCES `employee_struct_cat`, 
  `is_edit_all` TINYINT NOT NULL DEFAULT 0,
  `is_display_all` TINYINT NOT NULL DEFAULT 0
);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('name', 'Full Name', 2, 1, 1, 1, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('DOB', 'Date of Birth', 3, 1, 1, 1, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('communication_addr', 'Communication Address', 2, 1, 1, 1, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('permanant_addr', 'Permanant Address', 2, 1, 1, 1, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `max_lenght`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('mobile', 'Mobile Number', 1, 12, 0, 1, 1, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `max_lenght`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('emergency_contact', 'Emergency Contact', 1, 12, 1, 3, 1, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('designation', 'Designation', 2, 1, 2, 0, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('team', 'Team', 2, 1, 2, 0, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('joined_on', 'Joining Date', 3 , 1, 2, 0, 1);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `max_lenght`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('bank_accnt', 'Salary Account Number', 2, 20, 0, 4, 0, 0);

INSERT INTO `employee_struct` (`col_name`, `col_desc`, `col_type`, `max_lenght`, `required`, `category`, `is_edit_all`, `is_display_all`) VALUES ('pan_no', 'PAN Number', 2, 10, 0, 4, 0, 0);


CREATE TABLE IF NOT EXISTS `employee` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);


DROP TRIGGER IF EXISTS `add_employee_column`;
DELIMITER //
CREATE TRIGGER `add_employee_column` AFTER INSERT ON `employee_struct`
 FOR EACH ROW BEGIN
  DECLARE mysql_type VARCHAR(255);
  DECLARE col_name VARCHAR(255);

  SET col_name = NEW.`col_name`;
  
  IF NEW.`required`=1 THEN
    ALTER TABLE `employee` ADD COLUMN col_name varchar(255) NOT NULL;
    ELSE
    ALTER TABLE `employee` ADD COLUMN col_name varchar(255);
  END IF;
END
//
DELIMITER ;


DELIMITER //
CREATE PROCEDURE `add_emp_column` (IN col_name varchar(10), IN mysql_type varchar(10), OUT result varchar(100))
BEGIN
  SET @queryText = CONCAT('ALTER TABLE `employee` ADD ', col_name , '   ', mysql_type);
  PREPARE query FROM @queryText;
  EXECUTE query;
END
//
DELIMITER ;

CALL `add_emp_column`(test, 'int')
--------------------------------------------------------------------------------------------
--
-- Table structure for table `employee`
--

CREATE TABLE IF NOT EXISTS `salary_struct_cat` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `cat` varchar(50) NOT NULL
);

INSERT INTO `salary_struct_cat` (`cat`) VALUES ('Earning');
INSERT INTO `salary_struct_cat` (`cat`) VALUES ('Deductible');
INSERT INTO `salary_struct_cat` (`cat`) VALUES ('Loan');


CREATE TABLE IF NOT EXISTS `salary_struct` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `col_name` varchar(20) NOT NULL,
  `col_desc` varchar(255) NOT NULL,
  `col_type` varchar(10) NOT NULL REFERENCES `type_master`,
  `max_lenght` integer DEFAULT 0,
  `required` TINYINT NOT NULL DEFAULT 0,
  `default_val` integer DEFAULT 0,
  `category` varchar(20) REFERENCES `salary_struct_cat`, 
  `is_edit_all` TINYINT NOT NULL DEFAULT 0,
  `is_display_all` TINYINT NOT NULL DEFAULT 0
);

INSERT INTO `salary_struct` (`col_name`, `col_desc`, `col_type`, `required`, `default_val`, `category`, `is_edit_all`, `is_display_all`) VALUES ('basic', 'Basic Salary', 1, 1, 0, 1, 0, 1);

INSERT INTO `salary_struct` (`col_name`, `col_desc`, `col_type`, `required`, `default_val`, `category`, `is_edit_all`, `is_display_all`) VALUES ('HRA', 'HRA', 1, 1, 10000, 1, 0, 1);

INSERT INTO `salary_struct` (`col_name`, `col_desc`, `col_type`, `required`, `default_val`, `category`, `is_edit_all`, `is_display_all`) VALUES ('conveyence', 'Conveyence', 1, 0, 1000, 1, 0, 1);

INSERT INTO `salary_struct` (`col_name`, `col_desc`, `col_type`, `required`, `default_val`, `category`, `is_edit_all`, `is_display_all`) VALUES ('medical', 'Medical Expense', 1, 0, 1200, 1, 0, 1);

INSERT INTO `salary_struct` (`col_name`, `col_desc`, `col_type`, `required`, `default_val`, `category`, `is_edit_all`, `is_display_all`) VALUES ('pt', 'Professional Tax', 4, 1, 12.5, 2, 0, 1);

INSERT INTO `salary_struct` (`col_name`, `col_desc`, `col_type`, `required`, `default_val`, `category`, `is_edit_all`, `is_display_all`) VALUES ('tds', 'TDS', 4, 1, 10, 2, 0, 1);


CREATE TABLE IF NOT EXISTS `salary` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `employee_id` int(20) NOT NULL REFERENCES employee(`id`),
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `leave_type` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `desc` varchar(255) NOT NULL,
  `default` int(10) NOT NULL DEFAULT 0,
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

INSERT INTO `leave_type` (`desc`, `default`) VALUES ('Monthly', '2');
INSERT INTO `leave_type` (`desc`, `default`) VALUES ('Vacation Leave ', '0');

CREATE TABLE IF NOT EXISTS `leaves` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `employee_id` int(20) NOT NULL REFERENCES employee(`id`),
  `leave_type` int(20) NOT NULL,
  `from_date` timestamp NOT NULL default '0000-00-00 00:00:00',
  `to_date` timestamp NOT NULL default '0000-00-00 00:00:00',
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `user_id` int(50) NOT NULL, 
  `name` varchar(255) NOT NULL,
  `email` varchar(255) NOT NULL,
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `salary_slip_struct` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `title` varchar(255) NOT NULL,
  `desc` varchar(255) NOT NULL,
  `value` varchar(255) NOT NULL,
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'

);

INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Employee Details', 'Payment Account', 'bank_accnt', 'employee');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Employee Details', 'PAN', 'pan', 'employee');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Employee Details', 'Employee Name', 'name', 'employee');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Employee Details', 'Designation', 'designation', 'employee');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Employee Details', 'Team', 'team', 'employee');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Earnings', 'Basic', 'basic', 'salary');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Earnings', 'HRA', 'HRA', 'salary');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Earnings', 'Travel Allowance', 'conveyence', 'salary');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Earnings', 'Medical', 'medical', 'salary');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Deductions', 'PT', 'pt', 'salary');
INSERT INTO `salary_slip_struct` (`title`,`desc`, `value`) VALUES ('Deductions', 'TDS', 'tds', 'salary');























--------------------------------------------------------------------------------------------
--
-- Table structure for table `employee`
--



CREATE TABLE IF NOT EXISTS `employee_personal_details` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `name` varchar(255) NOT NULL, 
  `DOB` timestamp NOT NULL default '0000-00-00 00:00:00',
  `mobile` int(10) NOT NULL, 
  `permanant_address` varchar(255) NOT NULL, 
  `communication_address` varchar(255) NOT NULL, 
  `deleted` tinyint(4) default '0',
  `updated` timestamp NOT NULL default CURRENT_TIMESTAMP on update CURRENT_TIMESTAMP,
  `created` timestamp NOT NULL default '0000-00-00 00:00:00'
);

CREATE TABLE IF NOT EXISTS `employee_professional_details` (
  `designation` varchar(255) NOT NULL,
  `team` varchar(255) NOT NULL,
  `joined_on` timestamp NOT NULL default '0000-00-00 00:00:00',
  `pan` int(10) NOT NULL DEFAULT 0,
  `salary_mode` varchar(20) NOT NULL DEFAULT 'cheque',
  `account_no` int(30) NOT NULL DEFAULT 0,
  `vacation_leaves` int(5) NOT NULL DEFAULT 0,
);


CREATE TABLE IF NOT EXISTS `employee_master_table` (
  `id` int(20) NOT NULL auto_increment PRIMARY KEY,
  `belongs_to` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `desc` varchar(255),
  `obj_type` varchar(255) NOT NULL DEFAULT 'char',
  `required` INT(1) NOT NULL DEFAULT 0
);

INSERT INTO employee_struct (`name`, `desc`, `required`) VALUES ('ename', 'Employee Name', 1);
INSERT INTO employee_struct (`name`, `desc`,`obj_type`, `required`) VALUES ('DOB', 'Date of Birth', 'date', 1);
INSERT INTO employee_struct (`name`, `desc`,`obj_type`) VALUES ('mobile', 'Mobile Number', 'int');
INSERT INTO employee_struct (`name`, `desc`) VALUES ('permanant_address', 'permanant_address');
INSERT INTO employee_struct (`name`, `desc`, `required`) VALUES ('communication_address', 'communication_address', 1);
INSERT INTO employee_struct (`name`, `desc`) VALUES ('designation', 'designation');
INSERT INTO employee_struct (`name`, `desc`) VALUES ('team', 'team');
INSERT INTO employee_struct (`name`, `desc`,`obj_type`) VALUES ('joined_on', 'joined_on', 'date');
INSERT INTO employee_struct (`name`, `desc`,`obj_type`) VALUES ('pan', 'pan', 'int');
INSERT INTO employee_struct (`name`, `desc`) VALUES ('salary_mode', 'salary_mode');
INSERT INTO employee_struct (`name`, `desc`,`obj_type`) VALUES ('account_no', 'account_no', 'int');
INSERT INTO employee_struct (`name`, `desc`) VALUES ('vacation_leaves', 'vacation_leaves', 'int');

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

