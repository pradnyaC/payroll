import datetime
import simplejson
import functions
import yaml
from string import Template

""" Users functions """
def new_user(db, userid, name, mail):
  if not db.query("SELECT * FROM users WHERE userid = %s", userid):
    if not db.query("SELECT * FROM users WHERE email LIKE %s", mail): 
      return db.execute("INSERT INTO users (userid, name, email) VALUES (%s, %s, %s)", userid, name, mail)
    else:
      return db.execute("UPDATE users SET userid = %s, name = %s WHERE email LIKE %s", userid, name, mail)

def get_user_details(db, userid):
  return db.get("SELECT * FROM users WHERE userid = %s", userid)

def get_user_by_email(db, email):
  result = db.get("SELECT userid FROM users WHERE email like %s", email)
  if result:
    return result['userid']
  else:
    return 0

def get_user_by_empid(db, empid):
  return db.get("SElECT * FROM users WHERE empid = %s", empid)

""" Employee functions """
def get_employee_by_email(db, email):
  return db.get("SELECT * FROM employee WHERE email like %s", email)

def new_employee(db, details):
  db.execute("INSERT INTO employee (details) VALUES (%s)", simplejson.dumps(details))
  empid = db.get("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()']
  if get_user_by_email(db, details['email']):
    db.execute("UPDATE users SET empid = %s WHERE email = %s", empid, details['email'])
  else:
    db.execute("INSERT INTO users (empid, email) VALUES (%s, %s)", empid, details['email'])
  return empid

def edit_emp_details(db, empid, details):
  return db.execute("UPDATE employee SET details = %s WHERE empid = %s", simplejson.dumps(details), empid)

def delete_employee(db, empid):
  db.execute("UPDATE employee SET deleted = 1 WHERE empid = %s", empid)

def get_emp_details(db, empid):
  result = db.query("SELECT details FROM employee WHERE empid = %s AND deleted = 0", empid)
  if result:
    return simplejson.loads(result[0]['details'])
  else:
    return {}

def get_all_empids(db):
  result = db.query("SELECT empid FROM employee WHERE deleted = 0")
  if result:
    return [ r['empid' ]for r in result ]
  else:
    return []

def get_all_emp_details(db):
  result = db.query("SELECT * FROM employee WHERE deleted = 0")
  details = {}
  if result:
    for r in result:
      details[r['empid']] = simplejson.loads(r['details'])
    return details
  else:
    return {} 


""" Salary functions """
def new_salary(db, empid, sal_details):
  return db.execute("INSERT INTO salary (empid, details) VALUES (%s, %s)", empid, simplejson.dumps(sal_details))

def edit_salary(db, empid, sal_details):
  return db.execute("UPDATE salary SET details = %s WHERE empid = %s", simplejson.dumps(sal_details), empid)

def delete_salary(db, empid):
  return db.execute("UPDATE salary SET deleted = 1 WHERE empid = %s", empid)

def get_salary_details(db, empid):
  result = db.query("SELECT details FROM salary WHERE empid = %s", empid)
  if result:
    return simplejson.loads(result[0]['details'])
  else:
    return {}

def get_all_salary_details(db):
  result = db.query("SELECT * FROM salary")
  details = {}
  if result:
    for r in result:
      details[r['empid']] = simplejson.loads(r['details'])
    return details
  else:
    return {} 


""" Leave functions """
def add_leave(db, empid, date):
  leave_date = functions.get_date(date)
  key = str(empid) + ":" + str(leave_date.month) + ":" + str(leave_date.year)
  result = db.get("SELECT details FROM leaves WHERE leave_key LIKE %s", str(key))

  if result:
    leaves = simplejson.loads(result['details'])
    leaves.append(date)
    return db.execute("UPDATE leaves SET details = %s WHERE leave_key LIKE %s", simplejson.dumps(leaves), str(key))
  else:
    return db.execute("INSERT INTO leaves (leave_key, details) VALUES (%s, %s)", str(key), simplejson.dumps([date]))

def delete_leave(db, empid, date):
  leave_date = functions.get_date(date)
  key = str(empid) + ":" + str(leave_date.month) + ":" + str(leave_date.year)
  
  leaves = db.query("SELECT * FROM leaves WHERE leave_key LIKE %s", str(key))
  if leaves:
    leaves = simplejson.loads(leaves)
    if not leaves.count(date) == 0:
      leaves.remove(date)

def get_leaves(db, empid, month=datetime.date.today().month, year=datetime.date.today().year):
  key = str(empid) + ":" + str(month) + ":" + str(year)
  result = db.get("SELECT * FROM leaves WHERE leave_key LIKE %s ", key)
  if result:
    return simplejson.loads(result['details'])
  else:
    return []


""" Expense funtions """
def add_expesne(db, empid, details, month=datetime.date.today().month):
  expenseid = str(empid) + ":" + str(month)
  if not db.query("SELECT * FROM expenses WHERE expenseid = %s", expenseid):
    db.execute("INSERT INTO expenses (expenseid, details) VALUES (%s, %s)", expenseid, simplejson.dumps(details))
  else:
    db.execute("UPDATE expenses SET details = %s WHERE expenseid LIKE %s", simplejson.dumps(details), expenseid)

def get_expenses(db, empid, month=datetime.date.today().month):
  expenseid = str(empid) + ":" + str(month)
  result = db.get("SELECT details FROM expenses WHERE expenseid = %s", expenseid)
  if result:
    return {empid: simplejson.loads(result['details'])}
  else:
    return {}


"""  Salary Slip """
def calc_salary(db, empid, formula_yml="formulas.yml"):
  formula = yaml.load(open(formula_yml))['salary']
  salary_details = get_salary_details(db, empid)
  formula = Template(formula)
  sal = eval(formula.substitute(salary_details))

