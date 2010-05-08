import datetime
import simplejson
import functions
import yaml
from string import Template
from calendar import Calendar

month_30 = [2, 4, 6, 9, 11]
month_31 = [1, 3, 5, 7, 8, 10, 12]


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

  #insert a entry into vacation leave accouts table
  db.execute("INSERT INTO vacation_leave_accnt (empid, leaves) VALUES (%s, 0)", empid)
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
  if db.query("SELECT details FROM salary WHERE empid = %s", empid):
    return db.execute("UPDATE salary SET details = %s WHERE empid = %s", simplejson.dumps(sal_details), empid)
  else:
    db.execute("INSERT INTO salary (empid, details) VALUES (%s, %s)", empid, simplejson.dumps(sal_details))

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


""" Vacation Leave functions """
def get_vl_accounts(db):
  return db.query("SELECT * FROM vacation_leave_accnt")

def add_vacation_leave(db, empid, from_date, to_date):
  start_date = functions.get_date(from_date)
  key = str(empid) + ":VL:" + str(start_date.month) + ":" + str(start_date.year)
  result = db.get("SELECT details FROM leaves WHERE leave_key LIKE %s", str(key))

  if result:
    leaves = simplejson.loads(result['details'])
    leaves.append((from_date, to_date))
    return db.execute("UPDATE leaves SET details = %s WHERE leave_key LIKE %s", simplejson.dumps(leaves), str(key))
  else:
    return db.execute("INSERT INTO leaves (leave_key, details) VALUES (%s, %s)", str(key), simplejson.dumps([(from_date, to_date)]))


def get_month_vl(db, empid, month=datetime.date.today().month, year=datetime.date.today().year):
  key = str(empid) + ":VL:" + str(month) + ":" + str(year)
  result = db.get("SELECT * FROM leaves WHERE leave_key LIKE %s ", key)
  if result:
    return simplejson.loads(result['details'])
  else:
    return []
  
def calc_vacation_leave_accnt(db, empid, month=datetime.date.today().month, year=datetime.date.today().year):
  vaction_leaves = get_month_vl(db, empid, month, year)
  vl = 0
  end_date = datetime.datetime(year, month, (31, 30)[month in month_30])
  for (from_date,to_date) in vaction_leaves:
    to_date = functions.get_date(to_date)
    from_date = functions.get_date(from_date)

    #Check if to_date is in the same month or not
    if not to_date.month == month: to_date = end_date

    vl = vl + (to_date - from_date).days + 1
  print vl
  return vl


""" Monthly leaves functions """
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

def calc_month_leave_accnt(db, empid, month=datetime.date.today().month, year=datetime.date.today().year):
  leaves = get_leaves(db, empid, month, year)
  cal = Calendar()
  working_days = [w for w in cal.iterweekdays()]
  total_working_days = len(working_days) + len(get_working_days(db)) - len(get_holidays(db))
  total_leaves = (0, len(leaves) - 2)[len(leaves) > 2]
  total_pay_days = total_working_days - total_leaves
  return {'working_days':total_working_days, 'total_leaves':total_leaves}



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
  result = {}
  val_dict = {}
  
  #accumulate all information needed to calculate salary
  salary_details = get_salary_details(db, empid)
  expense_details = get_expenses(db, empid)[empid]
  leave_details = calc_month_leave_accnt(db, empid)
  val_dict = dict(val_dict, **salary_details)
  val_dict = dict(val_dict, **expense_details)
  val_dict = dict(val_dict, **leave_details)

  #calculate expressions
  formula_set = yaml.load(open(formula_yml))
  for key in formula_set:
    res = {}
    for i in formula_set[key]:
      formula = formula_set[key][i]
      res[i] = eval(Template(formula).substitute(val_dict))
      val_dict[i] = res[i]
    val_dict[key] = res['z']
    result[key] = res['z']
  
  #prepare result dict
  emp_details = get_emp_details(db, empid)
  val_dict = dict(val_dict, **emp_details)
  return dict(val_dict, **result)


""" Holiday functions """

def add_holiday(db, holiday, reason=""):
  holiday = functions.get_date(holiday)
  return db.execute("INSERT INTO holidays (holiday, reason) VALUES (%s, %s)", holiday, reason)

def get_holidays(db, month=datetime.date.today().month, year=datetime.date.today().year):
  start_date = datetime.date(year, month, 1)
  end_date = datetime.date(year, month, (31, 30)[month in month_30])
  result = db.query("SELECT holiday FROM holidays WHERE holiday BETWEEN %s AND %s", start_date, end_date)

  if result:
    return [h['holiday'] for h in result]
  else:
    return []

def add_working_day(db, date, month=datetime.date.today().month, year=datetime.date.today().year):
  key = str(month) + ":" + str(year)
  result = db.get("SELECT details FROM working_sat WHERE satid LIKE %s", str(key))

  if result:
    sats = simplejson.loads(result['details'])
    sats.append(date)
    return db.execute("UPDATE working_sat SET details = %s WHERE satid LIKE %s", simplejson.dumps(sats), str(key))
  else:
    return db.execute("INSERT INTO working_sat (satid, details) VALUES (%s, %s)", str(key), simplejson.dumps([date]))

def get_working_days(db, month=datetime.date.today().month, year=datetime.date.today().year):
  key = str(month) + ":" + str(year)
  result = db.get("SELECT * FROM working_sat WHERE satid LIKE %s ", key)
  if result:
    return simplejson.loads(result['details'])
  else:
    return []

