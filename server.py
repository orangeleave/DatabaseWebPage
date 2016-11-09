#!/usr/bin/env python2.7

import os
from sqlalchemy import *
from sqlalchemy.pool import NullPool
from flask import Flask, request, render_template, g, redirect, Response, session

tmpl_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
app = Flask(__name__, template_folder=tmpl_dir)


#
# The following is a dummy URI that does not connect to a valid database. You will need to modify it to connect to your Part 2 database in order to use the data.
#
# XXX: The URI should be in the format of: 
#
#     postgresql://USER:PASSWORD@w4111a.eastus.cloudapp.azure.com/proj1part2
#
# For example, if you had username gravano and password foobar, then the following line would be:
#
#     DATABASEURI = "postgresql://gravano:foobar@w4111a.eastus.cloudapp.azure.com/proj1part2"
#
DATABASEURI = ""


#
# This line creates a database engine that knows how to connect to the URI above.
#
engine = create_engine(DATABASEURI)

#
# Example of running queries in your database
# Note that this will probably not work if you already have a table named 'test' in your database, containing meaningful data. 
# This is only an example showing you how to run queries in your database using SQLAlchemy.
#
# engine.execute("""CREATE TABLE IF NOT EXISTS test (
#   id serial,
#   name text
# );""")
# engine.execute("""INSERT INTO test(name) VALUES ('grace hopper'), ('alan turing'), ('ada lovelace');""")


@app.before_request
def before_request():
  """
  This function is run at the beginning of every web request 
  (every time you enter an address in the web browser).
  We use it to setup a database connection that can be used throughout the request.

  The variable g is globally accessible.
  """
  try:
    g.conn = engine.connect()
  except:
    print "uh oh, problem connecting to database"
    import traceback; traceback.print_exc()
    g.conn = None

@app.teardown_request
def teardown_request(exception):
  """
  At the end of the web request, this makes sure to close the database connection.
  If you don't, the database could run out of memory!
  """
  try:
    g.conn.close()
  except Exception as e:
    pass


#
# @app.route is a decorator around index() that means:
#   run index() whenever the user tries to access the "/" path using a GET request
#
# If you wanted the user to go to, for example, localhost:8111/foobar/ with POST or GET then you could use:
#
#       @app.route("/foobar/", methods=["POST", "GET"])
#
# PROTIP: (the trailing / in the path is important)
# 
# see for routing: http://flask.pocoo.org/docs/0.10/quickstart/#routing
# see for decorators: http://simeonfranklin.com/blog/2012/jul/1/python-decorators-in-12-steps/
#
@app.route('/')
def index():
  """
  request is a special object that Flask provides to access web request information:

  request.method:   "GET" or "POST"
  request.form:     if the browser submitted a form, this contains the data in the form
  request.args:     dictionary of URL arguments, e.g., {a:1, b:2} for http://localhost?a=1&b=2

  See its API: http://flask.pocoo.org/docs/0.10/api/#incoming-request-data
  """

  # DEBUG: this is debugging code to see what request looks like


  print request.args
  return render_template("index.html")

  #
  # Flask uses Jinja templates, which is an extension to HTML where you can
  # pass data to a template and dynamically generate HTML based on the data
  # (you can think of it as simple PHP)
  # documentation: https://realpython.com/blog/python/primer-on-jinja-templating/
  
  # You can see an example template in templates/index.html
  
  # context are the variables that are passed to the template.
  # for example, "data" key in the context variable defined below will be 
  # accessible as a variable in index.html:
  
  #     # will print: [u'grace hopper', u'alan turing', u'ada lovelace']
  #     <div>{{data}}</div>
      
  #     # creates a <div> tag for each element in data
  #     # will print: 
  #     #
  #     #   <div>grace hopper</div>
  #     #   <div>alan turing</div>
  #     #   <div>ada lovelace</div>
  #     #
  #     {% for n in data %}
  #     <div>{{n}}</div>
  #     {% endfor %}
  
  # context = dict(data = rows)


  #
  # render_template looks in the templates/ folder for files.
  # for example, the below file reads template/index.html
  #

#
# This is an example of a different path.  You can see it at:
# 
#     localhost:8111/another
#
# Notice that the function name is another() rather than index()
# The functions for each app.route need to have different names
#


def search(table, constraint):
  cursor = g.conn.execute("SELECT * FROM" + " " + table + " " + "WHERE" + " " + constraint)
  printCols = []
  printRows = []
  for dbCols in cursor:
    for dbRows in dbCols:
      printCols.append(dbRows)
    printRows.append(printCols)
    printCols = []
  cursor.close()
  return printRows

# customer webpage
@app.route('/customer_location', methods=['POST'])
def customer_location():
  location = request.form['location']
  data = g.conn.execute("SELECT hname, room_provide.location, capacity, room_provide.rtype, price, phone FROM hotel_branch join room_provide on hotel_branch.location = room_provide.location Where room_provide.location = '%s'" % location)
  context = dict(data = data, rv = ['Hotel_Name', 'Location', 'Capacity', 'Room_Type', 'Price', 'Phone'], att = session['username'], status = session['status'], att2 = session['att2'])
  return render_template("customer.html", **context)

@app.route('/customer_number', methods=['POST'])
def customer_number():
  number = request.form['number']
  t = "transaction_make_manage"
  c = "trans_number = '%s' AND anumber = '%s'" % (number, session['status'][0][0])
  context = dict(data = search(t, c), rv = ['Trans_number', 'Account', 'Amount', 'Date', 'cssn', 'Location'], att = session['username'], status = session['status'], att2 = session['att2'])
  return render_template("customer.html", **context)


@app.route('/customer_type', methods=['POST'])
def customer_type():
  type = request.form['type']
  t = "room_provide"
  c = "rtype = '%s'" %type
  context = dict(data = search(t, c), rv = ['rnumber', 'rtype', 'price', 'location'], att = session['username'], status = session['status'], att2 = session['att2'])
  return render_template("customer.html", **context)

@app.route('/customer_cssn', methods=['POST'])
def customer():
  cssn = request.form['cssn']
  t = "check_in_and_out_table_generate"
  c = "cssn = '%s'" %cssn
  context = dict(data = search(t, c), rv = ['cssn', 'indate', 'outdata', 'rtype', 'rnumber', 'trans_number'], att = session['username'], status = session['status'], att2 = session['att2'])
  return render_template("customer.html", **context)

@app.route('/customer_history', methods=['POST'])
def customer_history():
  checkin = request.form['checkin']
  checkout = request.form['checkout']
  c1 = ""
  c2 = ""
  if(checkin):
    c1 = "indate = '%s'" % checkin
  if(checkout):
    c2 = "outdate = '%s'" % checkout
    if(checkin):
      c2 = " AND " + c2
  c = c1 + c2
  req = "a.anumber = '%s'"
  if(c):
    req = c + "AND " + req
  data = g.conn.execute("SELECT c.cssn, rtype, rnumber, trans_number, anumber FROM check_in_and_out_table_generate c JOIN customer_account a on c.cssn = a.cssn WHERE " + req % session['status'][0][0])
  if(data):
    context = dict(data = data, rv = ['SSN', 'Room Type', 'Room Number', 'Trans_number', 'Account_number'], att = session['username'], status = session['status'], att2 = session['att2'])
    return render_template("customer.html", **context)
  return render_template("customer.html")

@app.route('/login', methods=['POST'])
def login():
  name = request.form['name']
  if(name):
    t = "customer_account"
    c = "anumber = '%s'" %name
    results = search(t, c)
    if(results):
      t2 = "membership"
      c2 = "anumber = '%s'" %name
      session['status'] = search(t2, c2)
      rv = ['anumber', 'credits', 'level', 'discount']
      session['att2'] = rv
      result = results[0][1]
      session['username'] = result
      context = dict(att = session['username'], status = session['status'], att2 = session['att2'])
      return render_template("customer.html", **context)
  return render_template("index.html")

@app.route('/logout')
def logout():
  session.pop('username', None)
  session.pop('status', None)
  session.pop('att2', None)
  return render_template("index.html")

@app.route('/customer_check', methods=['POST'])
def customer_check():
  ssn = request.form['ssn']
  checkin = request.form['checkin']
  checkout = request.form['checkout']
  t = "check_in_and_out_table_generate"
  c1 = ""
  c2 = ""
  c3 = ""
  if(ssn):
    c1 = "cssn = '%s'" %ssn
  if(checkin):
    c2 = "indate = '%s'" %checkin
    if(ssn):
      c2 = " and " + c2
  if(checkout):
    c3 = "outdate = '%s'" %checkout
    if(ssn or checkin):
      c3 = " and " + c3
  c = c1 + c2 + c3
  if(c == ""):
    return render_template("customer.html")
  context = dict(data = search(t, c), rv = ['SSN', 'CheckIn Date', 'CheckOut Date', 'Room Type', 'Room Number', 'Trans_number'])
  return render_template("customer.html", **context)


#search function for manager (interesting queries in pj1.2)


@app.route('/manager')
def manager():
  return render_template("manager.html")



@app.route('/manager_dis', methods=['POST'])
def man_discount():
  dis = request.form['dis']
  results = g.conn.execute("SELECT cname, credits, level, discount FROM customer_account join membership on customer_account.anumber = membership.anumber WHERE discount = '%s';" % dis)
  rv = ['cname', 'credits', 'level', 'discount']
  context = dict(data = results, att = rv)
  return render_template("manager.html", **context)

@app.route('/manager_rtype', methods=['POST'])
def man_rtype():
  rtype = request.form['rtype']
  results = g.conn.execute("SELECT Customer_account.cssn, cname, tnumber, email FROM customer_account join check_in_and_out_table_generate on customer_account.cssn = check_in_and_out_table_generate.cssn WHERE rtype = '%s';" % rtype)
  rv = ['cssn', 'cname', 'tnumber', 'email']
  context = dict(data = results, att = rv)
  return render_template("manager.html", **context)

@app.route('/manager_budget', methods=['POST'])
def man_budget():
  size = request.form['size']
  if(size):
    results = g.conn.execute("SELECT AVG(budget) FROM department_has WHERE size >= %s" % size)
    if(results):
      rv = ['Target_Avg_budget_of_target_size_range$']
      context = dict(data = results, att = rv)
      return render_template("manager.html", **context)
  return render_template("manager.html")

@app.route('/manager_dept', methods=['POST'])
def man_dept():
  dept = request.form['dept']
  results = g.conn.execute("SELECT d.dname, e.ename, e.address, e.tnumber, e.salary FROM works_in w, department_has d, employee e WHERE w.dname = d.dname and w.essn = e.essn and d.dname= '%s'" % dept)
  rv = ['Dept Name', 'Employee Name', 'Emp Address', 'Emp Telephone', 'Salary']
  context = dict(data = results, att = rv)
  return render_template("manager.html", **context)

@app.route('/manager_check', methods=['POST'])
def manager_check():
  ssn = request.form['ssn']
  checkin = request.form['checkin']
  checkout = request.form['checkout']
  t = "check_in_and_out_table_generate"
  c1 = ""
  c2 = ""
  c3 = ""
  if(ssn):
    c1 = "cssn = '%s'" %ssn
  if(checkin):
    c2 = "indate = '%s'" %checkin
    if(ssn):
      c2 = " and " + c2
  if(checkout):
    c3 = "outdate = '%s'" %checkout
    if(ssn or checkin):
      c3 = " and " + c3
  c = c1 + c2 + c3
  if(c == ""):
    return render_template("manager.html")
  context = dict(data = search(t, c), att = ['SSN', 'CheckIn Date', 'CheckOut Date', 'Room Type', 'Room Number', 'Trans_number'])
  return render_template("manager.html", **context)

if __name__ == "__main__":
  import click

  @click.command()
  @click.option('--debug', is_flag=True)
  @click.option('--threaded', is_flag=True)
  @click.argument('HOST', default='0.0.0.0')
  @click.argument('PORT', default=8111, type=int)

  def run(debug, threaded, host, port):
    """
    This function handles command line parameters.
    Run the server using:

        python server.py

    Show the help text using:

        python server.py --help

    """
    app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?RT'
    HOST, PORT = host, port
    print "running on %s:%d" % (HOST, PORT)
    app.run(host=HOST, port=PORT, debug=debug, threaded=threaded)

  run()
