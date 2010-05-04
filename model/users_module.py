import time
from datetime import datetime
from datetime import date
import functions
import yaml

types_file = open("data_types.yml")
types = yaml.load(types_file)
types_file.close()


""" User Functions """
def add_user(db, user_id, name, email):
  return db.execute("INSERT INTO users (user_id, name, email) VALUES (%s, %s, %s)", user_id, name, email)

def get_user_details(db, user_id):
  return db.get("SELECT * FROM users WHERE user_id = %s", user_id)


""" Employee functions """
def get_employee_fields(db):
  fields = db.query("SELECT * FROM employee_struct ORDER BY id")
  for f in fields:
    f['col_type'] = types[int(f['col_type'])]['type']
  return fields

def get_emp_field_type(db):
  fields = db.query("SELECT col_name, col_type FROM employee_struct ORDER BY id")
  details = {}
  for f in fields:
    details[f['col_name']] = types[int(f['col_type'])]['type']
  return details

def add_employee_fields(db, current_user, fields_details):
  db.execute("INSERT INTO employee_struct (name, desc, obj_type, required) VALUES")

def new_employee(db, current_user, employee_details):
  field_types = get_emp_field_type(db)
  keys = [key for key in employee_details]

  query = "INSERT INTO employee ("
  query += ",".join(keys)
  query += " ) VALUES ( " + ",".join(["%s" for u in keys]) + " )"

  values = []
  for key in keys:
    if field_types[key] == "date":
      values.append(datetime.strptime(employee_details[key], '%d-%m-%Y'))
    else:
      values.append(employee_details[key])
  db.execute(query, *values)
  
  return db.get("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()']

def edit_employee_details(db, employee_id, employee_details):
  keys = [key for key in employee_details]
  field_types = get_emp_field_type(db)

  values = []
  query = "UPDATE employee SET "
  i = 0
  for key in keys:
    if field_types[key] == "date":
      values.append(datetime.strptime(employee_details[key], '%Y-%m-%d %H:%M:%S'))
    else:
      values.append(employee_details[key])
    query += str(key) + "= %s"
    i += 1
    if i < len(keys): query += " , "
  
  query += " WHERE id = "+ employee_id
  return db.execute(query, *values)

def get_employee_details(db, employee_id):
  return db.get("SELECT * FROM employee WHERE id = %s", employee_id)

def get_all_employees(db):
  return db.query("SELECT * FROM employee WHERE deleted = 0")

def parse_employee_details(employee_dict):
  details = {}
  for key in employee_dict:
    if key.count("value") > 0:
      details[key.split(".")[1]] = employee_dict[key]
  return details


""" Salary Functions """
def get_salary_fields(db):
  fields =  db.query("SELECT * FROM salary_struct ORDER BY id")
  for f in fields:
    f['col_type'] = types[int(f['col_type'])]['type']
  return fields

def get_salary_fields_types(db):
  fields =  db.query("SELECT col_name, col_type FROM salary_struct ORDER BY id")
  details = {}
  for f in fields:
    details[f['col_name']] = types[int(f['col_type'])]['type']
  return details

def add_salary(db, employee_id, sal_details):
  sal_types = get_salary_fields_types(db)
  keys = [key for key in sal_details]

  query = "INSERT INTO salary (employee_id, "
  query += ",".join(keys)
  query += " ) VALUES ( " + employee_id + ", "
  query += ",".join(["%s" for u in keys]) + " )"

  values = []
  for key in keys:
    if sal_types[key] == "date":
      values.append(datetime.strptime(sal_details[key], '%d-%m-%Y'))
    else:
      values.append(sal_details[key])
  db.execute(query, *values)

def edit_salary(db, emp_id, sal_details):
  sal_types = get_salary_fields_types(db)
  keys = [key for key in sal_details]

  values = []
  query = "UPDATE salary SET "
  i = 0

  for key in keys:
    if sal_types[key] == "date":
      values.append(datetime.strptime(sal_details[key], '%Y-%m-%d %H:%M:%S'))
    else:
      values.append(sal_details[key])
    query += str(key) + "= %s"
    i += 1
    if i < len(keys): query += " , "
  
  query += " WHERE employee_id = " + emp_id
  return db.execute(query, *values)

def get_salary_details(db, emp_id):
  return db.get("SELECT * FROM salary WHERE employee_id = %s", emp_id)


""" Leave functions"""

def get_leave_types(db):
  return db.query("SELECT * FROM leave_type ORDER BY id")

def add_leaves(db, employee_id, leave_from, leave_to, leave_type):
  leave_from = datetime.strptime(leave_from, '%d/%m/%Y')
  leave_to = datetime.strptime(leave_to, '%d/%m/%Y')
  
  return db.execute("INSERT INTO leaves (employee_id, from_date, to_date, leave_type ) VALUES (%s, %s, %s, %s)", employee_id, leave_from, leave_to, leave_type)

def get_leave_details(db, emp_id, from_date=None, to_date=None):
  query_string = "SELECT * FROM leaves WHERE employee_id = %s "
  if not from_date:
    return db.query(query_string, emp_id)
  else:
    query_string = query_string + " AND from_date > %s"
    if not to_date:
      return db.query(query_string, emp_id, from_date, datetime.now())
    else:
      query_string = query_string + " AND to_date < %s"
      return db.query(query_string, emp_id, from_date, to_date)

def get_month_leaves(db, emp_id, month):
  from_date =  date(date.today().year, month, 1)
  try: 
    to_date = date(date.today().year, month, 31)
  except:
    to_date = date(date.today().year, month, 30)
  return db.query("SELECT count(*) AS count FROM leaves WHERE employee_id = %s AND from_date >= %s and to_date <= %s", emp_id, from_date, to_date)

def get_sal_slip_titles(db):
  titles = db.query("SELECT distinct title FROM salary_slip_struct where deleted = 0 ORDER BY title")
  return [t['title'] for t in titles]


def get_sal_slip_struct(db):
  sal_slip = db.query("SELECT * FROM salary_slip_struct where deleted = 0 ORDER BY title")
  sal_struct = {}
  title = ""
  for s in sal_slip:
    if not title == s['title']:
      title = s['title']
      sal_struct[title] = []
    sal_struct[title].append(s)
  return sal_struct

def get_sal_slip_fields(db):
  fields = db.query("SELECT value FROM salary_slip_struct where deleted = 0 ORDER BY title")
  return [f['value'] for f in fields]

def calculate_salary(db, month, emp_id=None):
  if not emp_id:
    employees = get_all_employees(db)
    emp_ids = [e['id'] for e in employees]
  else:
    emp_ids = [emp_id]

  slip_struct = get_sal_slip_struct(db)
  slip_fields = get_sal_slip_fields(db)
  sal_sheet = {}
  for uid in emp_ids:
    details = {}
    
    #Add employee details
    emp_details = get_employee_details(db, uid)
    if emp_details:
      for key in emp_details:
        details[key] = emp_details[key]
    
    #Add salary details to the sheet
    sal_details = get_salary_details(db, uid)
    if sal_details:
      for key in sal_details:
        details[key] = sal_details[key]

    #Add leave details to the sheet
    leave_details = get_month_leaves(db, emp_id, month)
    if leave_details:
      details['total_leaves'] = leave_details[0]['count']
    else:
      details['total_leaves'] = 0
    details['emp_id'] = uid
    
    sal_slip = {}
    for title in slip_struct:
      fields = slip_struct[title]
      for f in fields:
        if details.has_key(str(f['value'])):
          if not sal_slip.has_key(title):
            sal_slip[title] = {}
          sal_slip[title][f['desc']] = details[f['value']]
      sal_slip['total_leaves'] = details['total_leaves']
      sal_slip['emp_id'] = details['emp_id']
    sal_sheet[uid] = sal_slip
  
  return sal_sheet

def user_login(request):
  consumer = Consumer(request, OpenIDStore())
  try:
    auth_request = consumer.begin("https://www.google.com/accounts/o8/id")
  except DiscoveryFailure:
    print 'The OpenID was invalid'


if __name__ == "__main__":
  login(urllib2.Request("https://www.google.com/accounts/o8/id"))
  consumer = consumer.Consumer(Session, None)
