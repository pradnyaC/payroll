import datetime
import simplejson

""" Users functions """
def new_user(db, userid, name, mail):
  if not db.execute("SELECT * FROM users WHERE userid = %s", userid):
    return db.execute("INSERT INTO users (userid, name, email) VALUES (%s, %s, %s)", userid, name, mail)

def get_user_details(db, userid):
  return db.get("SELECT * FROM users WHERE userid = %s", userid)

def get_user_by_email(db, email):
  result = db.get("SELECT userid FROM users WHERE email like %s", email)
  if result:
    return result['userid']
  else:
    return 0

""" Employee functions """

def get_employee_by_email(db, email):
  return db.get("SELECT * FROM employee WHERE email like %s", email)

def new_employee(db, empid, details):
  return db.execute("INSERT INTO employee (empid, details) VALUES (%s, %s)", empid, simplejson.dumps(details))

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



""" Leave functions """
def add_leave(db, empid, date):
  date = functions.get_date(date)
  key = str(empid) + ":" + date.month + ":" + date.year
  leaves = db.query("SELECT * FROM leaves WHERE key = %s", key)
  if leaves:
    return db.execute("UPDATE leaves SET details = %s WHERE key = %s", simplejson.dumps((simpljson.loads(leaves)).append(date)), key)
  else:
    return db.execute("INSERT INTO leaves (key, details) VALUES (%s, %s)", key, simplejson.dumps([date]))

def delete_leave(db, empid, date):
  date = functions.get_date(date)
  key = str(empid) + ":" + date.month + ":" + date.year
  leaves = db.query("SELECT * FROM leaves WHERE key = %s", key)
  if leaves:
    leaves = simplejson.loads(leaves)
    if not leaves.count(date) == 0:
      leaves.remove(date)

def get_leaves(db, empid, month=datetime.date.today().month, year=datetime.date.today().year):
  key = str(empid) + ":" + str(month) + ":" + str(year)
  leaves = db.query("SELECT * FROM leaves WHERE key = %s", key)
  if leaves:
    return simplejson.loads(leaves)
  else:
    return []


"""  Salary Slip """
