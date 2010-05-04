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
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+/new)", NewSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+)/edit", EditSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/leave", LeaveHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary_calc", SalaryCalcHandler),
      (r"" + config['application_configuration']['base_path'] + "/admin/emp_struct", UserAdminHandler),
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
    employees = users_module.get_all_employees(self.db)
    self.render("employees.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin'], employees=employees)

class NewEmployeeHandler(BaseHandler):
  def get(self):
    employee_fields = users_module.get_employee_fields(self.db)
    self.render("new_employee.html", current_user = self.get_current_user(), is_an_admin=int(self.get_current_user()['is_admin'], post_data=self.request.arguments, employee_fields=employee_fields, errors="")

  def post(self):
    errors = []
    post_data = self.request.arguments
    employee_fields = users_module.get_employee_fields(self.db)

    for field in employee_fields:
      if int(field['required']) == 1:
        if not self.request.arguments.has_key(field['col_name']) : errors.append("Please Enter "+ field['col_desc'])

    post_data = self.request.arguments
    employee_details = {}
    user_fields = [f['col_name'] for f in employee_fields]
    
    for key in post_data:
      if key in user_fields:
        employee_details[key] = post_data[key][0]
    """
    ### Specifically salary code ##
    if not self.request.arguments.has_key("salary_mode") : errors.append("Please Enter salary_mode")
    else:
      if self.get_argument("salary_mode") == "bank":
        pay_mode = "bank"
        if not self.request.arguments.has_key("account_no"): 
          accnt_no = None
          errors.append("Please Enter accnt number")
        else:
          accnt_no = self.get_argument("account_no")
      else:
        pay_mode = "cheque"
        accnt_no = None
    ### ###
    """
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("new_employee.html", current_user = self.get_current_user(), employee_fields=employee_fields, employee_details=employee_details, errors=errors_message)
    else:
      employee_id = users_module.new_employee(self.db, employee_fields, employee_details)
      
      #redirect to the page with all users
      self.redirect("/payroll/salary/"+str(employee_id)+"/new")

class EditEmployeeHandler(BaseHandler):
  def get(self, employee_id):
    employee_details = users_module.get_employee_details(self.db, employee_id)
    employee_fields = users_module.get_employee_fields(self.db)

    self.render("edit_employee.html", current_user = self.get_current_user(), employee_id=employee_id, employee_fields=employee_fields, employee_details=employee_details, errors="")


  def post(self, employee_id):
    errors = []
    post_data = self.request.arguments
    employee_fields = users_module.get_employee_fields(self.db)
    user_fields = [f['col_name'] for f in employee_fields]
    
    for field in employee_fields:
      if int(field['required']) == 1:
        if not self.request.arguments.has_key(field['col_name']) : errors.append("Please Enter "+ field['col_desc'])

    post_data = self.request.arguments
    employee_details = {}
    for key in post_data:
      if key in user_fields:
        employee_details[key] = post_data[key][0]
    """
    ### Specifically salary code ##
    if not self.request.arguments.has_key("salary_mode") : errors.append("Please Enter salary_mode")
    else:
      if self.get_argument("salary_mode") == "bank":
        pay_mode = "bank"
        if not self.request.arguments.has_key("account_no"): 
          accnt_no = None
          errors.append("Please Enter accnt number")
        else:
          accnt_no = self.get_argument("account_no")
      else:
        pay_mode = "cheque"
        accnt_no = None
    ### ###
    """
    
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("edit_user.html", current_user = self.get_current_user(), employee_id=employee_id, employee_fields=employee_fields, employee_details=employee_details, errors=errors_message)
    else:
      users_module.edit_employee_details(self.db, employee_id, employee_details)
    
      #redirect to the page with all users
      self.redirect("/payroll/salary/"+employee_id+"/edit")

class NewSalaryHandler(BaseHandler):
  def get(self, emp_id):
    emp_id = emp_id.split("/new")[0]
    emp_name = users_module.get_employee_details(self.db, emp_id)['name']
    sal_fields = users_module.get_salary_fields(self.db)
    
    self.render("salary.html", current_user = self.get_current_user(), emp_id=emp_id, emp_name=emp_name, sal_fields=sal_fields, errors="")

  def post(self, emp_id):
    emp_id = emp_id.split("/new")[0]
    errors = []
    employee_details = users_module.get_employee_details(self.db, emp_id)
    emp_name = employee_details['name']
    sal_fields = users_module.get_salary_fields(self.db)
    
    for sal in sal_fields:
      if int(sal['required']) == 1:
        if not self.request.arguments.has_key(sal['col_name']) : errors.append("Please Enter "+ sal['col_desc'])

    post_data = self.request.arguments
    sal_details = {}
    fields = [s['col_name'] for s in sal_fields]
    for key in post_data:
      if key in fields:
        sal_details[key] = post_data[key][0]

    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("salary.html", current_user = self.get_current_user(), emp_id=emp_id, emp_name=emp_name, sal_details=sal_details, sal_fields=sal_fields, errors=errors_message)
    else:
      users_module.add_salary(self.db, emp_id, sal_details )

      #redirect to the page with all users
      self.redirect("/payroll/employees")

class EditSalaryHandler(BaseHandler):
  def get(self, emp_id):
    sal_details = users_module.get_salary_details(self.db, emp_id)
    emp_name = users_module.get_employee_details(self.db, emp_id)['name']
    sal_fields = users_module.get_salary_fields(self.db)
    
    self.render("edit_salary.html", current_user = self.get_current_user(), emp_id=emp_id, emp_name=emp_name, sal_details=sal_details, sal_fields=sal_fields, errors="")

  def post(self, emp_id):
    errors = []
    emp_details = users_module.get_employee_details(self.db, emp_id)
    emp_name = emp_details['name']
    sal_fields = users_module.get_salary_fields(self.db)

    for sal in sal_fields:
      if int(sal['required']) == 1:
        if not self.request.arguments.has_key(sal['col_name']) : errors.append("Please Enter "+ sal['col_desc'])

    post_data = self.request.arguments
    sal_details = {}
    fields = [s['col_name'] for s in sal_fields]
    for key in post_data:
      if key in fields:
        sal_details[key] = post_data[key][0]

    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("edit_salary.html", current_user = self.get_current_user(), emp_id=emp_id, emp_name=emp_name, sal_details=sal_details, sal_fields=sal_fields, errors=errors_message)
    else:
      users_module.edit_salary(self.db, emp_id, sal_details)
      
      #redirect to the page with all users
      self.redirect("/payroll/employees")

class LeaveHandler(BaseHandler):
  def get(self):
    user = self.get_current_user()
    leave_types = users_module.get_leave_types(self.db)
    print users_module.get_leave_details(self.db, 1)
    self.render("leave_sheet.html", current_user = self.get_current_user(), user=user, leave_types=leave_types, errors="")

  def post(self):
    user = self.get_current_user()
    errors = []
    if not self.request.arguments.has_key("from_date") : errors.append("Please enter a From date")
    if not self.request.arguments.has_key("to_date") : errors.append("Please enter a From date")
    if not self.request.arguments.has_key("leave_type") : errors.append("Please select leave_type")

    post_data = self.request.arguments
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("leave_sheet.html", current_user = self.get_current_user(), user=user, post_data=self.request.arguments, errors=errors_message)
    else:
      users_module.add_leaves(self.db, user['id'], self.get_argument("from_date"), self.get_argument("from_date"), self.get_argument("leave_type"))

      #redirect to the page with all users
      self.redirect("/payroll/employees")

class UserAdminHandler(BaseHandler):
  def get(self):
    emp_fields = users_module.get_employee_fields(self.db)
    self.render("user_admin.html", current_user = self.get_current_user(), emp_fields=emp_fields, errors="")

  #def post(self):


class SalaryCalcHandler(BaseHandler):
  def get(self, emp_id=None):
    sal_sheet = users_module.calculate_salary(self.db, 4, emp_id)
    slip_titles = users_module.get_sal_slip_titles(self.db)
    self.render("salary_sheet.html", current_user = self.get_current_user(), sal_sheet=sal_sheet, slip_titles=slip_titles)

def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
