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

def new_user(db, name, dob, mobile, permanant_address, communication_address, designation, team, joining, pan, pay_mode, accnt_no):
  dob = datetime.strptime(dob, '%d/%m/%Y')
  joining = datetime.strptime(joining, '%d/%m/%Y')
  
  db.execute("INSERT INTO users (name, dob, mobile, permanant_address, communication_address, designation, team, joined_on, pan, pay_mode, account_no) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", name, dob, mobile, permanant_address, communication_address, designation, team, joining, pan, pay_mode, accnt_no)
  return db.get("SELECT id FROM users WHERE name = %s AND dob = %s" )
  
def edit_user(db, user_id, name, dob, mobile, permanant_address, communication_address, designation, team, joining, pan, pay_mode, accnt_no):
  dob = datetime.strptime(dob, '%Y-%m-%d %H:%M:%S')
  joining = datetime.strptime(joining, '%Y-%m-%d %H:%M:%S')

  return db.execute("UPDATE users SET name = %s, dob = %s, mobile = %s, permanant_address = %s, communication_address = %s, designation = %s, team = %s, joined_on = %s, pan = %s, pay_mode = %s, account_no = %s WHERE id = %s", name, dob, mobile, permanant_address, communication_address, designation, team, joining, pan, pay_mode, accnt_no, user_id)

def get_user_details(db, user_id):
  return db.get("SELECT * FROM users WHERE id = %s", user_id)

def get_salary_details(db, user_id):
  return db.get("SELECT * FROM salary_structure WHERE user_id = %s", user_id)

def get_all_users(db):
  return db.query("SELECT * FROM users WHERE deleted = 0")

def add_salary(db, user_id, basic, hra, conveyence, medical, pt, tds, monthly_leaves, vacation_leaves):
  db.execute("INSERT INTO salary_structure (user_id, basic, hra, conveyence, medical, pt, tds, monthly_leaves, vacation_leaves) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)", user_id, basic, hra, conveyence, medical, pt, tds, monthly_leaves, vacation_leaves)

def edit_salary(db, user_id, basic, hra, conveyence, medical, pt, tds, monthly_leaves, vacation_leaves):
  db.execute("UPDATE salary_structure SET basic=%s, HRA=%s, conveyence=%s, medical=%s, pt=%s, tds=%s, monthly_leaves=%s, vacation_leaves=%s WHERE user_id =%s", basic, hra, conveyence, medical, pt, tds, monthly_leaves, vacation_leaves, user_id)

def add_leaves(db, user_id, month, monthly_total, monthly_dates, vacation_total, vacation_dates):
  return db.execute("INSERT INTO leaves (user_id, month, monthly_total, monthly_dates, vacation_total, vacation_dates) VALUES (%s, %s, %s, %s, %s, %s)", user_id, month, monthly_total, monthly_dates, vacation_total, vacation_dates)

def get_leave_details(db, user_id, month=None):
  if not month:
    return db.query("SELECT * FROM leaves WHERE user_id = %s", user_id)
  else:
    return db.query("SELECT * FROM leaves WHERE user_id = %s and month = %s", user_id, lower(month))

def calculate_salary(db, month):
  users = get_all_users(db)
  user_ids = [for u['id'] in users]

  sal_sheet = {}
  for uid in user_ids:
    sal_details = get_salary_details(db, uid)
    leave_details = get_leave_details(db, user_id, month)[0]
    sal_sheet[uid] = dict(sal_details, **leave_details)
    
    
def user_login(request):
  consumer = Consumer(request, OpenIDStore())
  try:
    auth_request = consumer.begin("https://www.google.com/accounts/o8/id")
  except DiscoveryFailure:
    print 'The OpenID was invalid'


if __name__ == "__main__":
  login(urllib2.Request("https://www.google.com/accounts/o8/id"))
  consumer = consumer.Consumer(Session, None)
