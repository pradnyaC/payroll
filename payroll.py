# -*- coding: utf-8 -*-

import inspect
import logging
import os.path
import re
import math
import tornado.auth
import tornado.database
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.escape
import unicodedata
from tornado.options import define, options
import mail
import yaml
import MySQLdb
import datetime
from datetime import datetime
import sys
 
from openid.store.memstore import MemoryStore
from openid.consumer import consumer
from openid.consumer.discover import OpenIDServiceEndpoint
from openid.extensions import ax

import sys
sys.path.append('./model')
import emp_module
import users_module
import urlparse
import test1 
from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler

config_file = open("config.yml")
config = yaml.load(config_file)
config_file.close()

define("port", default=8888, help="run on the given port", type=int)
define("mysql_host", default=config['database_configuration']['host'] + ":" + str(config['database_configuration']['port']), help="prep database host")
define("mysql_database", default=config['database_configuration']['database'], help="prep database name")
define("mysql_user", default=config['database_configuration']['username'], help="prep database user")
define("mysql_password", default=config['database_configuration']['password'], help="prep database password")


class Application(tornado.web.Application):
  def __init__(self):
    handlers = [
      (r"" + config['application_configuration']['base_path'] + "/", HomeHandler),
      (r"" + config['application_configuration']['base_path'] + "/home", HomeHandler),
      (r"" + config['application_configuration']['base_path'] + "/login", LoginHandler),
      (r"" + config['application_configuration']['base_path'] + "/login/finish", FinishHandler),
      (r"" + config['application_configuration']['base_path'] + "/employees", EmployeeHandler),
      (r"" + config['application_configuration']['base_path'] + "/employee/new", NewEmployeeHandler),
      (r"" + config['application_configuration']['base_path'] + "/employee/([0-9]+)/edit", EditEmployeeHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary", SalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+/new)", NewSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+)/edit", EditSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/leaves", LeaveHandler),
      (r"" + config['application_configuration']['base_path'] + "/leave/new", AddLeaveHandler),
      (r"" + config['application_configuration']['base_path'] + "/expenses", ExpenseHandler),
      (r"" + config['application_configuration']['base_path'] + "/expense/new", NewExpenseHandler),
      (r"" + config['application_configuration']['base_path'] + "/expense/edit", EditExpenseHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary_calc", SalaryCalcHandler),
      ]
      
    settings = dict(
      template_path=os.path.join(os.path.dirname(__file__), "templates"),
      static_path=os.path.join(os.path.dirname(__file__), "static"),
      xsrf_cookies=True,
      cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
      login_url=config['application_configuration']['login_url']
    )
    tornado.web.Application.__init__(self, handlers, **settings)

    # Have one global connection to the blog DB across all handlers
    self.db = tornado.database.Connection(
      host=options.mysql_host, database=options.mysql_database,
      user=options.mysql_user, password=options.mysql_password)


class BaseHandler(tornado.web.RequestHandler):
  @property
  def db(self):
    return self.application.db
  
  def get_current_user(self):
    f = open("production_code")
    code = f.read()
    f.close()
    exec(code)
    if not user_id: user_id = 0
    if int(user_id) == 0:
      pass
    else:
      user = emp_module.get_user_details(self.db, user_id)
#      if not user:
#        user_name = self.get_user_name(int(user_id))
#        users_module.new_user(self.redisInstance, user_id, user_name)
      return user

class HomeHandler(BaseHandler):
  def get(self):
    self.render("home.html", current_user = self.get_current_user())

class LoginHandler(BaseHandler, test1.OpenIDRequestHandler):
  def get(self):
    self.render("login.html")
    
  def post(self):
    """Handles login requests."""
    openid_url = "https://www.google.com/accounts/o8/site-xrds?ns=2&hd=pagalguy.com"
    
    if not openid_url:
      self.report_error('Please enter an OpenID URL.')
      return

    oidconsumer = self.getConsumer()
    try:
        request = oidconsumer.begin(openid_url)
    except consumer.DiscoveryFailure, exc:
        print "error in discovery", exc
    else:
        if request is None:
            print 'No OpenID services found'
        else:
            trust_root = "http://localhost:8888/payroll"
            return_to = "http://localhost:8888/payroll/login/finish"

            fetch_request = ax.FetchRequest()
            fetch_request.add(ax.AttrInfo("http://axschema.org/namePerson/first", required=True, alias="first_name"))
            fetch_request.add(ax.AttrInfo("http://axschema.org/namePerson/last", required=True, alias="last_name"))
            fetch_request.add(ax.AttrInfo("http://schema.openid.net/contact/email", required=True, alias="email"))
            
            request.addExtension(fetch_request)
            redirect_url = request.redirectURL(trust_root, return_to)#, immediate=True)
            self.set_status(302)
            self.set_header('Location', redirect_url)

class FinishHandler(BaseHandler, test1.OpenIDRequestHandler):
  """Handle a redirect from the provider."""
  def get(self):
    oidconsumer = self.getConsumer()
    url = "http://localhost:8888/payroll/login/finish"

    query = {}
    for arg in self.request.arguments:
      query[arg] = self.request.arguments[arg][0]
    
    current_user_id = query['openid.claimed_id'].split("id=")[1]
    query['openid.identity'] = "https://www.google.com/accounts/o8/user-xrds?uri=" + query['openid.claimed_id']
    query['openid.claimed_id'] = "https://www.google.com/accounts/o8/user-xrds?uri=" + query['openid.claimed_id']

    info = oidconsumer.complete(query, url)
    if str(info.status) == "success":
      response = ax.FetchResponse.fromSuccessResponse(info)
      user_details = response.getExtensionArgs()

      #Store user data
      self.set_secure_cookie("current_user", current_user_id)
      username = user_details['value.first_name'] + "  " + user_details['value.last_name'].split("@")[0]
      emp_module.new_user(self.db, current_user_id, username, user_details['value.email'])
      self.redirect("/payroll/home")
      
class EmployeeHandler(BaseHandler):
  def get(self):
    employees = emp_module.get_all_emp_details(self.db)
    self.render("employees.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), employees=employees)

class NewEmployeeHandler(BaseHandler):
  def get(self):
    self.render("new_employee.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']))

  def post(self):
    post_data = self.request.arguments
    employee_details = {}
    for key in post_data: 
      if not str(key) == "_xsrf" and not str(key) == "save":
        employee_details[key] = post_data[key][0]
    employee_id = emp_module.new_employee(self.db, employee_details)

    #redirect to the page with all users
    self.redirect("/payroll/salary/"+str(employee_id)+"/new")


class EditEmployeeHandler(BaseHandler):
  def get(self, employee_id):
    employee_details = emp_module.get_emp_details(self.db, employee_id)

    self.render("edit_employee.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), employee_id=employee_id, employee_details=employee_details, errors="")

  def post(self, employee_id):
    post_data = self.request.arguments
    employee_details = {}
    for key in post_data: 
      if not str(key) == "_xsrf" and not str(key) == "save":
        employee_details[key] = post_data[key][0]

    emp_module.edit_emp_details(self.db, employee_id, employee_details)

    #redirect to the page with all users
    self.redirect("/payroll/salary/"+str(employee_id)+"/edit")

class SalaryHandler(BaseHandler):
  def get(self):
    salaries = emp_module.get_all_salary_details(self.db)
    self.render("salaries.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), salaries=salaries)


class NewSalaryHandler(BaseHandler):
  def get(self, empid):
    empid = empid.split("/new")[0]
    self.render("new_salary.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), empid=empid)

  def post(self, empid):
    empid = empid.split("/new")[0]
    post_data = self.request.arguments
    sal_details = {}
    for key in post_data: 
      if not str(key) == "_xsrf" and not str(key) == "save":
        sal_details[key] = post_data[key][0]

    emp_module.new_salary(self.db, empid, sal_details)
    #redirect to the page with all users
    self.redirect("/payroll/employees")

class EditSalaryHandler(BaseHandler):
  def get(self, empid):
    empid = empid.split("/edit")[0]
    sal_details = emp_module.get_salary_details(self.db, empid)
    try:
      empname = emp_module.get_emp_details(self.db, empid)['emp_name']
    except:
      empname = None
    
    self.render("edit_salary.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), empid=empid, empname=empname, sal_details=sal_details)

  def post(self, empid):
    empid = empid.split("/edit")[0]
    post_data = self.request.arguments
    sal_details = {}
    for key in post_data: 
      if not str(key) == "_xsrf" and not str(key) == "save":
        sal_details[key] = post_data[key][0]

    emp_module.edit_salary(self.db, empid, sal_details)

    #redirect to the page with all users
    self.redirect("/payroll/employees")

class LeaveHandler(BaseHandler):
  def get(self):
    empid = self.get_current_user()['empid']
    leaves = emp_module.get_leaves(self.db, empid)
    self.render("leaves.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), leaves=leaves)


class AddLeaveHandler(BaseHandler):
  def get(self):
    empid = self.get_current_user()['empid']
    self.render("new_leave.html", current_user = self.get_current_user(), empid=empid)

  def post(self):
    empid = self.get_current_user()['empid']
    emp_module.add_leave(self.db, empid, self.get_argument("leave_date"))

    #redirect to the page with all users
    self.redirect("/payroll/leaves")

class ExpenseHandler(BaseHandler):
  def get(self):
    empid = self.get_current_user()['empid']
    expenses = emp_module.get_expenses(self.db, empid)
    self.render("expenses.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), expenses=expenses)


class NewExpenseHandler(BaseHandler):
  def get(self):
    empid = self.get_current_user()['empid']
    self.render("new_expense.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), empid=empid)

  def post(self):
    empid = self.get_current_user()['empid']
    post_data = self.request.arguments
    expense_details = {}
    for key in post_data: 
      if not str(key) == "_xsrf" and not str(key) == "save":
        expense_details[key] = post_data[key][0]
    
    emp_module.add_expesne(self.db, empid, expense_details)
    #redirect to the page with all users
    self.redirect("/payroll/expenses")


class EditExpenseHandler(BaseHandler):
  def get(self):
    empid = self.get_current_user()['empid']
    expense_details = emp_module.get_expenses(self.db, empid)
    try: expense_details = expense_details[empid]
    except: expense_details = {}
    self.render("edit_expense.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin']), empid=empid, expense_details=expense_details)

  def post(self):
    empid = self.get_current_user()['empid']
    post_data = self.request.arguments
    expense_details = {}
    for key in post_data: 
      if not str(key) == "_xsrf" and not str(key) == "save":
        expense_details[key] = post_data[key][0]
    
    emp_module.add_expesne(self.db, empid, expense_details)
    #redirect to the page with all users
    self.redirect("/payroll/expenses")


class SalaryCalcHandler(BaseHandler):
  def get(self, emp_id=None):
    sal_sheet = emp_module.calc_salary(self.db, 1)
    #slip_titles = users_module.get_sal_slip_titles(self.db)
    #self.render("salary_sheet.html", current_user = self.get_current_user(), sal_sheet=sal_sheet, slip_titles=slip_titles)

def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
