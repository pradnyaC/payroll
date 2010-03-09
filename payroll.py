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
      (r"" + config['application_configuration']['base_path'] + "/user/new", NewUserHandler),
      (r"" + config['application_configuration']['base_path'] + "/user/([0-9]+)/edit", EditUserHandler),
      (r"" + config['application_configuration']['base_path'] + "/salary/([0-9]+)", NewSalaryHandler),
      (r"" + config['application_configuration']['base_path'] + "/users", UserHandler),
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
    self.render("new_user.html", post_data=self.request.arguments, errors="")

  def post(self):
    errors = []
    post_data = self.request.arguments
    if not self.request.arguments.has_key("name") : errors.append("Please Enter Employee Name")
    if not self.request.arguments.has_key("dob") : errors.append("Please Enter Date of Birth")
    if not self.request.arguments.has_key("mobile") : errors.append("Please Enter Contact Number")
    if not self.request.arguments.has_key("permanant_address") : errors.append("Please Enter permanant_address")
    if not self.request.arguments.has_key("communication_address") : errors.append("Please Enter communication_address")
    if not self.request.arguments.has_key("designation") : errors.append("Please Enter a Designation")
    if not self.request.arguments.has_key("team") : errors.append("Please Enter Team")
    if not self.request.arguments.has_key("joining") : errors.append("Please Enter joining date")
    if not self.request.arguments.has_key("pan"): pan = None
    else: pan = self.get_argument("pan")
    if not self.request.arguments.has_key("salary_mode") : errors.append("Please Enter salary_mode")
    else:
      if self.get_argument("salary_mode") == "bank":
        pay_mode = "bank"
        if not self.request.arguments.has_key("accnt"): 
          accnt_no = None
          errors.append("Please Enter accnt number")
        else:
          accnt_no = self.get_argument("accnt")
      else:
        pay_mode = "cheque"
        accnt_no = None

    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("new_user.html", post_data=self.request.arguments, errors=errors_message)
    else:
      user_id = users_module.new_user(self.db, self.get_argument("name"), self.get_argument("dob"), self.get_argument("mobile"),
      self.get_argument("permanant_address"), self.get_argument("communication_address"), self.get_argument("designation"), self.get_argument("team"), self.get_argument("joining"), pan, pay_mode, accnt_no)
      
      #redirect to the page with all users
      self.redirect("/payroll/salary/"+user_id)

class EditUserHandler(BaseHandler):
  def get(self, user_id):
    user_details = users_module.get_user_details(self.db, user_id)
    self.render("edit_user.html",user_id=user_id, user_details=user_details, errors="")

  def post(self, user_id):
    errors = []
    post_data = self.request.arguments
    if not self.request.arguments.has_key("name") : errors.append("Please Enter Employee Name")
    if not self.request.arguments.has_key("DOB") : errors.append("Please Enter Date of Birth")
    if not self.request.arguments.has_key("mobile") : errors.append("Please Enter Contact Number")
    if not self.request.arguments.has_key("permanant_address") : errors.append("Please Enter permanant_address")
    if not self.request.arguments.has_key("communication_address") : errors.append("Please Enter communication_address")
    if not self.request.arguments.has_key("designation") : errors.append("Please Enter a Designation")
    if not self.request.arguments.has_key("team") : errors.append("Please Enter Team")
    if not self.request.arguments.has_key("joined_on") : errors.append("Please Enter joining date")
    if not self.request.arguments.has_key("pan"): pan = None
    else: pan = self.get_argument("pan")
    if not self.request.arguments.has_key("pay_mode") : errors.append("Please Enter salary_mode")
    else:
      if self.get_argument("pay_mode") == "bank":
        pay_mode = "bank"
        if not self.request.arguments.has_key("account_no"): 
          accnt_no = None
          errors.append("Please Enter accnt number")
        else:
          accnt_no = self.get_argument("account_no")
      else:
        pay_mode = "cheque"
        accnt_no = None

    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      user_details = {}
      for key in post_data:
        user_details[key] = post_data[key][0]
      self.render("edit_user.html", user_id=user_id, user_details=user_details, errors=errors_message)
    else:
      users_module.edit_user(self.db, user_id, self.get_argument("name"), self.get_argument("DOB"), self.get_argument("mobile"), self.get_argument("permanant_address"), self.get_argument("communication_address"), self.get_argument("designation"), self.get_argument("team"), self.get_argument("joined_on"), pan, pay_mode, accnt_no)
    
      #redirect to the page with all users
      self.redirect("/payroll/salary/"+user_id+"/edit")

class NewSalaryHandler(BaseHandler):
  def get(self, user_id):
    user_details = users_module.get_user_details(self.db, user_id)
    self.render("salary.html", user=user_details, errors="")

  def post(self, user_id):
    errors = []
    if not self.request.arguments.has_key("basic") : errors.append("Please Enter basic salary")
    if not self.request.arguments.has_key("hra") : errors.append("Please Enter HRA")
    if not self.request.arguments.has_key("conveyence") : errors.append("Please Enter conveyence")
    if not self.request.arguments.has_key("medical") : errors.append("Please Enter medical")
    if not self.request.arguments.has_key("pt") : errors.append("Please Enter PT")
    if not self.request.arguments.has_key("tds") : errors.append("Please Enter TDS")
    if not self.request.arguments.has_key("monthly_leaves") : errors.append("Please Enter monthly_leaves")
    if not self.request.arguments.has_key("vacation_leaves") : errors.append("Please Enter vacation_leaves")

    user_details = users_module.get_user_details(self.db, user_id)
    
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      self.render("salary.html", user=user_details, post_data=self.request.arguments, errors=errors_message)
      #self.render("new_user.html", post_data=self.request.arguments, errors=errors_message)
    else:
      users_module.add_salary(self.db, user_id, self.get_argument("basic"), self.get_argument("hra"), self.get_argument("conveyence"), self.get_argument("medical"), self.get_argument("pt"), self.get_argument("tds"), self.get_argument("monthly_leaves"), self.get_argument("vacation_leaves"))
    
      #redirect to the page with all users
      self.redirect("/payroll/users")

class EditSalaryHandler(BaseHandler):
  def get(self, user_id):
    sal_details = users_module.get_salary_details(self.db, user_id)
    self.render("edit_salary.html", sal_details=sal_details, errors="")

  def post(self, user_id):
    errors = []
    if not self.request.arguments.has_key("basic") : errors.append("Please Enter basic salary")
    if not self.request.arguments.has_key("hra") : errors.append("Please Enter HRA")
    if not self.request.arguments.has_key("conveyence") : errors.append("Please Enter conveyence")
    if not self.request.arguments.has_key("medical") : errors.append("Please Enter medical")
    if not self.request.arguments.has_key("pt") : errors.append("Please Enter PT")
    if not self.request.arguments.has_key("tds") : errors.append("Please Enter TDS")
    if not self.request.arguments.has_key("monthly_leaves") : errors.append("Please Enter monthly_leaves")
    if not self.request.arguments.has_key("vacation_leaves") : errors.append("Please Enter vacation_leaves")
    
    if len(errors) > 0: 
      errors_message = "Following errors were encountered<ul>" + "".join([ "<li>" + error + "</li>" for error in errors]) + "</ul>"
      sal_details = {}
      for key in post_data:
        sal_details[key] = post_data[key][0]
      self.render("edit_salary.html", sal_details=sal_details, errors=errors_message)
    else:
      users_module.edit_salary(self.db, user_id, self.get_argument("basic"), self.get_argument("hra"), self.get_argument("conveyence"), self.get_argument("medical"), self.get_argument("pt"), self.get_argument("tds"), self.get_argument("monthly_leaves"), self.get_argument("vacation_leaves"))
    
      #redirect to the page with all users
      self.redirect("/payroll/users")

def main():
  tornado.options.parse_command_line()
  http_server = tornado.httpserver.HTTPServer(Application())
  http_server.listen(options.port)
  tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
  main()
