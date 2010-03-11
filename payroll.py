# -*- coding: utf-8 -*-
import linkedin  
import httplib

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

import sys
sys.path.append('./model')
import users_module

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
      (r"" + config['application_configuration']['base_path'] + "/login", GoogleHandler),
      (r"" + config['application_configuration']['base_path'] + "/users", UserHandler),
      (r"" + config['application_configuration']['base_path'] + "/user/new", NewUserHandler),
      (r"" + config['application_configuration']['base_path'] + "/user/([0-9]+)/edit", EditUserHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+/new)", NewSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+)/edit", EditSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/leave", LeaveHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary_calc", SalaryCalcHandler),
      (r"" + config['application_configuration']['base_path'] + "/users/admin", UserAdminHandler),
      ]
      
    settings = dict(
      template_path=os.path.join(os.path.dirname(__file__), "templates"),
      static_path=os.path.join(os.path.dirname(__file__), "static"),
      xsrf_cookies=True,
      cookie_secret="11oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
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
      return users_module.get_user_details(self.db, user_id)

class HomeHandler(BaseHandler):
  def get(self):
    self.render("home.html")

class GoogleHandler(tornado.web.RequestHandler, tornado.auth.GoogleMixin):
  @tornado.web.asynchronous
  def get(self):
    if self.get_argument("openid.mode", None):
        self.get_authenticated_user(self.async_callback(self._on_auth))
        return
    self.authenticate_redirect("")

  def _on_auth(self, user):
      print "user ", user
      if not user:
          self.authenticate_redirect("home")
          return
      # Save the user with, e.g., set_secure_cookie()
      self.render("login.html")
  
class LoginHandler(BaseHandler):
  def get(self):
    self.render("login.html")

  def post(self):
    request = self.get_argument("request_object")
    user = self.get_argument("user_login")
    users_module.user_login(self.session)
  
class UserHandler(BaseHandler):
  def get(self):
    users = users_module.get_all_users(self.db)
    self.render("users.html", users=users)
  
class NewUserHandler(BaseHandler):
  def get(self):
    user_compo = users_module.get_user_components(self.db)
    self.render("new_user.html", post_data=self.request.arguments, user_compo=user_compo, errors="")

  def post(self):
    errors = []
    post_data = self.request.arguments
    user_compo = users_module.get_user_components(self.db)

    for c in user_compo:
      if int(c['required']) == 1:
        if not self.request.arguments.has_key(c['name']) : errors.append("Please Enter "+ c['desc'])

    post_data = self.request.arguments
    user_details = {}
    user_fields = [u['name'] for u in user_compo]
    for key in post_data:
      if key in user_fields:
        user_details[key] = post_data[key][0]
    
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
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("new_user.html", user_compo=user_compo, user_details=user_details, errors=errors_message)
    else:
      user_id = users_module.new_user(self.db, user_compo, user_details)
      #users_module.edit_user1(self.db)
      
      #redirect to the page with all users
      self.redirect("/payroll/salary/"+str(user_id)+"/new")

class EditUserHandler(BaseHandler):
  def get(self, user_id):
    user_details = users_module.get_user_details(self.db, user_id)
    user_compo = users_module.get_user_components(self.db)
    self.render("edit_user.html",user_id=user_id, user_compo=user_compo, user_details=user_details, errors="")

  def post(self, user_id):
    errors = []
    post_data = self.request.arguments
    user_compo = users_module.get_user_components(self.db)

    for c in user_compo:
      if int(c['required']) == 1:
        if not self.request.arguments.has_key(c['name']) : errors.append("Please Enter "+ c['desc'])

    post_data = self.request.arguments
    user_details = {}
    user_fields = [u['name'] for u in user_compo]
    for key in post_data:
      if key in user_fields:
        user_details[key] = post_data[key][0]
    
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

    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("edit_user.html", user_id=user_id, user_compo=user_compo, user_details=user_details, errors=errors_message)
    else:
      users_module.edit_user(self.db, user_id, user_compo, user_details)
    
      #redirect to the page with all users
      self.redirect("/payroll/salary/"+user_id+"/edit")

class NewSalaryHandler(BaseHandler):
  def get(self, user_id):
    user_id = user_id.split("/new")[0]
    user_name = users_module.get_user_details(self.db, user_id)['name']
    sal_compo = users_module.get_sal_components(self.db)
    self.render("salary.html", user_id=user_id, user_name=user_name, sal_compo=sal_compo, errors="")

  def post(self, user_id):
    user_id = user_id.split("/new")[0]
    errors = []
    user_details = users_module.get_user_details(self.db, user_id)
    user_name = user_details['name']
    sal_compo = users_module.get_sal_components(self.db)
    
    for sal in sal_compo:
      if int(sal['required']) == 1:
        if not self.request.arguments.has_key(sal['name']) : errors.append("Please Enter "+ sal['desc'])

    post_data = self.request.arguments
    sal_details = {}
    sal_fields = [s['name'] for s in sal_compo]
    for key in post_data:
      if key in sal_fields:
        sal_details[key] = post_data[key][0]

    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("salary.html", user_id=user_id, user_name=user_name, sal_details=sal_details, sal_compo=sal_compo, errors=errors_message)
    else:
      users_module.add_salary(self.db, user_id, sal_compo, sal_details )

      #redirect to the page with all users
      self.redirect("/payroll/users")

class EditSalaryHandler(BaseHandler):
  def get(self, user_id):
    sal_details = users_module.get_salary_details(self.db, user_id)
    user_name = users_module.get_user_details(self.db, user_id)['name']
    sal_compo = users_module.get_sal_components(self.db)
    self.render("edit_salary.html", user_id=user_id, user_name=user_name, sal_details=sal_details, sal_compo=sal_compo, errors="")

  def post(self, user_id):
    errors = []
    user_details = users_module.get_user_details(self.db, user_id)
    user_name = user_details['name']
    sal_compo = users_module.get_sal_components(self.db)

    for sal in sal_compo:
      if int(sal['required']) == 1:
        if not self.request.arguments.has_key(sal['name']) : errors.append("Please Enter "+ sal['desc'])

    post_data = self.request.arguments
    sal_details = {}
    sal_fields = [s['name'] for s in sal_compo]
    for key in post_data:
      if key in sal_fields:
        sal_details[key] = post_data[key][0]
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("edit_salary.html", user_id=user_id, user_name=user_name, sal_details=sal_details, sal_compo=sal_compo, errors=errors_message)
    else:
      users_module.edit_salary(self.db, user_id, sal_compo, sal_details)
      
      #redirect to the page with all users
      self.redirect("/payroll/users")

class LeaveHandler(BaseHandler):
  def get(self):
    user = self.get_current_user()
    self.render("leave_sheet.html", user=user, errors="")

  def post(self):
    user = self.get_current_user()
    errors = []
    if not self.request.arguments.has_key("date") : errors.append("Please enter a date")
    if not self.request.arguments.has_key("leave_type") : errors.append("Please enter leave_type")

    post_data = self.request.arguments
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("leave_sheet.html", user=user, post_data=self.request.arguments, errors=errors_message)
    else:
      users_module.add_leaves(self.db, user['id'], self.get_argument("date"), self.get_argument("leave_type"))

      #redirect to the page with all users
      self.redirect("/payroll/users")

class UserAdminHandler(BaseHandler):
  def get(self):
    user_compo = users_module.get_user_components(self.db)
    self.render("user_admin.html", user_compo=user_compo, errors="")
  
  def post(self):
    

class SalaryCalcHandler(BaseHandler):
  def get(self):
    sal_sheet = users_module.calculate_salary(self.db, "jan")
    keys = [key for key in sal_sheet[0]]
    self.render("salary_sheet.html", sal_sheet=sal_sheet, keys=keys)

def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
