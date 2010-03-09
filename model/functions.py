from datetime import date, datetime, timedelta
from time import time,mktime
import math
import yaml
from BeautifulSoup import BeautifulSoup
from pytz import timezone
import pytz
import re

def mynaturalday(value, arg=None):
  """
  For date values that are tomorrow, today or yesterday compared to
  present day returns representing string. Otherwise, returns a string
  formatted according to settings.DATE_FORMAT.
  """
  try:
    value1 = date(value.year, value.month, value.day)
  except AttributeError:
    # Passed value wasn't a date object
    return value
  except ValueError:
    # Date arguments out of range
    return value
  delta = value1 - date.today()
  if delta.days == 0:
    return ('today')
  elif delta.days == 1:
    return ('tomorrow')
  elif delta.days == -1:
    return ('yesterday')
  elif delta.days == -2:
    return ('day before yesterday')
  elif delta.days < -2:
    return (''+str(abs(delta.days))+' days ago')

def generate_pagination(total,current_page,base_link,next_prev=True,limit=10):
  if(not total or not current_page or not base_link): return False
  total_pages = math.ceil(float(total)/float(limit))
  if(current_page > total_pages): return False
  txtPagesAfter = (" pages", " page")[total_pages==1]
  txt_page_list = ""
  min_val = (1, current_page-3)[(current_page - 3) < total_pages and (current_page-3) > 0]
  max_val = (current_page+3, total_pages) [(current_page + 3) > total_pages]
  page_links = ""
  first_page = ('','<a href="'+base_link+str(1)+'">&laquo;</a>')[current_page > 1]
  last_page = ('','<a href="'+base_link+str(int(total_pages))+'">&raquo;</a>')[current_page < total_pages]
  for i in range(int(min_val), int(max_val+1)):
    if(current_page==i):
      page_links = page_links + ' <span class="current">'+str(i)+'</span> '
    else:
      page_links = page_links + ' <a href="'+base_link+str(i)+'" class="page">'+str(i)+'</a> '
  if(next_prev):
    next = (' <a href="'+base_link+str(current_page + 1)+'">Next &gt;</a> ', "")[(current_page + 1) > total_pages]
    prev = (' <a href="'+base_link+str(current_page - 1)+'">&lt; Prev</a> ', "")[current_page - 1 <= 0 ]
  if(total_pages > 1): return '<span class="pagination">'+txt_page_list+first_page+prev+page_links+next+last_page+'</span>'
  else: return ""
  
def display_sponsors_dropdown(path, selected=None):
  sponsors_file = open(path)
  sponsors = yaml.load(sponsors_file)
  sponsors = sponsors['sponsors']
  sponsors_file.close()
  dropdown = '<select name="sponsor"><option></option>'
  for k, v in sponsors.items():
    dropdown = dropdown + '<option value="'+k+'"'
    if k == selected: dropdown = dropdown + ' selected="selected"'
    dropdown = dropdown + '>' + v['name'] + '</option>'
  dropdown = dropdown + '</select>'
  return dropdown
  
def get_sponsor_info(path, sponsor):
  sponsors_file = open(path)
  sponsors = yaml.load(sponsors_file)
  sponsors = sponsors['sponsors']
  sponsors_file.close()
  return sponsors[sponsor]
  
def file_get_contents(path):
  file_handle = open(path)
  file_contents = file_handle.read()
  file_handle.close()
  return file_contents
  
def sanitize_text(html):
  old_tags = ["<strong>","</strong>", "<em>","</em>", "<sup>","</sup>", "<sub>", "</sub>", "<img", "<p>", "</p>", "<br />", "<br>", "<span", "</span>"]
  new_tags = ["[[strong]]","[[/strong]]", "[[em]]","[[/em]]", "[[sup]]","[[/sup]]", "[[sub]]", "[[/sub]]", "[[img", "[[p]]", "[[/p]]","[[br /]]", "[[br /]]", "[[span", "[[/span]]"]
  textHTML = html
  for k,v in enumerate(old_tags):
    textHTML = textHTML.replace(v,new_tags[k])
  text = ''.join(BeautifulSoup(textHTML).findAll(text=True))
  for k,v in enumerate(new_tags):
    text = text.replace(v,old_tags[k])
  text = text.replace("<br>","<br />").replace("<br />","[[br /]]")
  text = text.lstrip("[[br /]]").rstrip("[[br /]]").replace("[[br /]]","<br />")
  text = BeautifulSoup(text).prettify()
  return text
  
def delete_row(db,table,key):
  return db.execute("UPDATE "+str(table)+" SET deleted = 1 WHERE id = %s",key)
  
def humanize_date_time(date_time, tz_original='GMT', tz='Asia/Kolkata'):
  fmt = '%B %d, %Y %I:%M %p'
  original_tz = timezone(tz_original)
  display_tz = timezone(tz)
  time_orig = datetime(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, date_time.second, tzinfo=original_tz)
  return time_orig.astimezone(display_tz).strftime(fmt)

def convert_to_timezone(date_time, tz_original='GMT', tz='Asia/Kolkata'):
  original_tz = timezone(tz_original)
  display_tz = timezone(tz)
  time_orig = datetime(date_time.year, date_time.month, date_time.day, date_time.hour, date_time.minute, date_time.second, tzinfo=original_tz)
  return time_orig.astimezone(display_tz)

def time_ago(date_time):
  #date_time = convert_to_timezone(date_time)
  current_time = int(time())
  original_time = int(mktime(date_time.timetuple()))
  time_difference = current_time - original_time
  output = ""
  days = int(float(time_difference)/float(86400))
  time_left = int(time_difference%86400)
  hours = int(float(time_left)/float(3600))
  time_left = int(time_left%3600)
  minutes = int(float(time_left)/float(60))
  seconds = int(time_left%60)
  if days < 1:
    output = ('',str(hours)+" hours")[hours > 0] + " " + ('',str(minutes)+" minute"+('s','')[minutes<=1])[minutes > 0] + " ago"
    if days < 1 and hours < 1 and minutes < 1:
      output = "A few seconds ago"
  elif days > 1 and days < 2:
    output = "yesterday at "+date_time.strftime("%I:%M %p")
  elif days > 2 and days < 7:
    output = ('',str(days)+" days")[days > 0] + " ago at "+date_time.strftime("%I:%M %p")
  else:
    output = humanize_date_time(date_time)
  return output
  
def generate_snipet(html, length = 100):
  text = ''.join(BeautifulSoup(html).findAll(text=True))
  text = text.replace('&nbsp;',' ');
  if len(text) <= length:
    text = text.lstrip()
    return text
  else:
    text = (' '.join(text[:length+1].split()[0:-1]) + "...")
    text = text.lstrip()
    return text
  
def create_left_menu(path, menu_yaml='menu.yml', active=-1):
  menu_data = yaml.load(open(menu_yaml))['menu']
  menu_data = [menu_data[i] for i in menu_data]
  left_menu_layout = open(path).read()
  menu_display = ''
  for i,menu in enumerate(menu_data):
    this_menu = left_menu_layout.replace('{TITLE}',menu['title']).replace('{URL}',menu['url']).replace('{ICON}',menu['icon'])
    if active == i: this_menu = this_menu.replace('{MENUCLASS}',' class="Active"')
    else: this_menu = this_menu.replace('{MENUCLASS}','')
    menu_display = menu_display + this_menu
  return menu_display
  
def create_chart(x_labels, values=[]):
  chart_data = open("templates/chart_data.json").read()
  chart_data = chart_data.replace('<<<<LABELS>>>>',str(x_labels))
  chart_elements = []
  for value in values:
    chart_element = '''{
                        "type":      "line",
                        "alpha":     0.5,
                        "colour":    "#888888",
                        "text":      "'''+ value[0] +'''",
                        "font-size": 10,
                        "values" : ''' + str(value[1:]) + ''',
                        "dot-style": {
                          "type": "solid-dot",
                          "dot-size": 5,
                          "dot-colour": "#FFF"
                        }
                      }'''
    chart_elements.append(chart_element)
  chart_data = chart_data.replace('<<<<ELEMENTS>>>>',','.join(chart_elements))
  return chart_data.replace("'",'"')