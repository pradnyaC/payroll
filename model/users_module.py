import openid
from openid.consumer.consumer import Consumer
from openid.consumer.discover import DiscoveryFailure
from openid.store.interface import OpenIDStore
from yadis import xri
import time
from datetime import datetime
import httplib
import urllib2
import consumer
import functions

def new_user(db, user_compo, user_details):
  user_fields = [u['name'] for u in user_compo]
  field_types = [u['obj_type'] for u in user_compo]
  values = []
  query = "INSERT INTO users ("
  query += ",".join(user_fields)
  query += " ) VALUES ( " + ",".join(["%s" for u in user_fields]) + " )"
  
  for field in user_fields:
    if field_types[user_fields.index(field)] == "date":
      values.append(datetime.strptime(user_details[field], '%d-%m-%Y'))
    else:
      values.append(user_details[field])
  db.execute(query, *values)
  
  return db.get("SELECT LAST_INSERT_ID()")['LAST_INSERT_ID()']

def edit_user(db, user_id, user_compo, user_details):
  user_fields = [u['name'] for u in user_compo]
  field_types = [u['obj_type'] for u in user_compo]

  values = []
  query = "UPDATE users SET "
  i = 0
  for field in user_fields:
    if field_types[user_fields.index(field)] == "date":
      values.append(datetime.strptime(user_details[field], '%Y-%m-%d %H:%M:%S'))
    else:
      values.append(user_details[field])
    query += str(field) + "= %s"
    i += 1
    if i < len(user_fields): query += " , "
  
  query += " WHERE id = "+ user_id
  return db.execute(query, *values)


def get_user_details(db, user_id):
  return db.get("SELECT * FROM users WHERE id = %s", user_id)

def get_all_users(db):
  return db.query("SELECT * FROM users WHERE deleted = 0")

def add_salary(db, user_id, sal_compo, sal_details):
  sal_fields = [s['name'] for s in sal_compo]
  field_types = [u['obj_type'] for u in sal_compo]
  values = []

  query = "INSERT INTO salary (user_id, "
  query += ",".join(sal_fields)
  query += " ) VALUES ( " + user_id + ", "
  query += ",".join(["%s" for u in sal_fields]) + " )"

  for field in sal_fields:
    if field_types[sal_fields.index(field)] == "date":
      values.append(datetime.strptime(sal_details[field], '%d-%m-%Y'))
    else:
      values.append(sal_details[field])

  return db.execute(query, *values)

def edit_salary(db, user_id, sal_compo, sal_details):
  sal_fields = [s['name'] for s in sal_compo]
  field_types = [sal['obj_type'] for sal in sal_compo]
  values = []
  query = "UPDATE salary SET "
  i = 0
  for field in sal_fields:
    if field_types[sal_fields.index(field)] == "date":
      values.append(datetime.strptime(sal_details[field], '%Y-%m-%d %H:%M:%S'))
    else:
      values.append(sal_details[field])
    query += str(field) + "= %s"
    i += 1
    if i < len(sal_fields): query += " , "
  
  query += " WHERE user_id = " + user_id
  return db.execute(query, *values)

def get_salary_details(db, user_id):
  return db.get("SELECT * FROM salary WHERE user_id = %s", user_id)


def add_leaves(db, user_id, leave_on, leave_type):
  leave_on = datetime.strptime(leave_on, '%d/%m/%Y')
  return db.execute("INSERT INTO leaves (user_id, leave_on, leave_type ) VALUES (%s, %s, %s)", user_id, leave_on, leave_type)

def get_leave_details(db, user_id, from_date=None, to_date=None):
  query_string = "SELECT * FROM leaves WHERE user_id = %s "
  if not from_date:
    return db.query(query_string, user_id)
  else:
    query_string = query_string + " AND leave_on BETWEEN %s AND %s"
    if not to_date:
      return db.query(query_string, user_id, from_date, datetime.now())
    else:
      return db.query(query_string, user_id, from_date, to_date)

def get_total_leaves(db, user_id, from_date=None, to_date=None):
  query_string = "SELECT count(*) AS count FROM leaves WHERE user_id = %s "
  if not from_date:
    return db.query(query_string, user_id)
  else:
    query_string = query_string + " AND leave_on BETWEEN %s AND %s"
    if not to_date:
      return db.query(query_string, user_id, from_date, datetime.now())
    else:
      return db.query(query_string, user_id, from_date, to_date)

def get_sal_components(db):
  result =  db.query("SELECT * FROM salary_struct ORDER BY id")
  return result

def get_user_components(db):
  return db.query("SELECT * FROM user_struct ORDER BY id")
  
def add_user_component(db, name, desc, ojb_type, val=0):
  db.execute("")

def calculate_salary(db, month):
  users = get_all_users(db)
  user_ids = [u['id'] for u in users]
  sal_compo = get_sal_components(db)
  sal_fields = [s['name'] for s in sal_compo]
  
  sal_sheet = []
  for uid in user_ids:
    details = {}
    
    #Add salary details to the sheet
    sal_details = get_salary_details(db, uid)
    if sal_details:
      for key in sal_details:
        if key in sal_fields:
          details[key] = sal_details[key]
      
    #Add leave details to the sheet
    if leave_details:
      leave_details = get_total_leaves(db, uid, '01/01/1000')
      details['total_leaves'] = leave_details[0]['count']
    else:
      details['total_leaves'] = 0
    details['user_id'] = uid
    
    
    sal_sheet.append(details)
    
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
