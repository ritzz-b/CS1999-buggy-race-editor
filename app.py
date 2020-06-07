from flask import Flask, render_template, request, jsonify
import sqlite3 as sql
app = Flask(__name__)

DATABASE_FILE = "database.db"
DEFAULT_BUGGY_ID = "1"

BUGGY_RACE_SERVER_URL = "http://rhul.buggyrace.net"


#------------------------------------------------------------
# the index page
#------------------------------------------------------------
@app.route('/')
def home():
   return render_template('index.html', server_url=BUGGY_RACE_SERVER_URL)

#------------------------------------------------------------
# creating a new buggy:
#  if it's a POST request process the submitted data
#  but if it's a GET request, just show the form
#------------------------------------------------------------
@app.route('/new', methods = ['POST', 'GET'])
def create_buggy():
  if request.method == 'GET': 
    con = sql.connect(DATABASE_FILE)
    con.row_factory = sql.Row
    cur = con.cursor()
    cur.execute("SELECT * FROM buggies")
    record = cur.fetchone();
    return render_template("buggy-form.html", buggy=None)
  elif request.method == 'POST':
    msg=""
    violations = ""
    qty_wheels = request.form['qty_wheels']
    if not qty_wheels.isdigit():
      msg = f"This is not a number: {qty_wheels}"
      return render_template("buggy-form.html", msg = msg)
    if int(qty_wheels) % 2 != 0 or int(qty_wheels) < 4:
      violations = "You have violated the rules!! "
    else: 
      violations = "The rules have been kept intact, good!" 
    flag_color = request.form['flag_color']
    msg = f"flag_color={flag_color}" 
    flag_pattern = request.form['flag_pattern']
    msg = f"flag_pattern={flag_pattern}"
    buggy_id = request.form['id']
    try:
      with sql.connect(DATABASE_FILE) as con:
        cur = con.cursor()
        if buggy_id.isdigit():
          cur.execute("UPDATE buggies set qty_wheels=?, flag_color=?, flag_pattern=? WHERE id=?", (qty_wheels, flag_color, flag_pattern, buggy_id))  
        else:
          cur.execute("INSERT INTO buggies (qty_wheels, flag_color, flag_pattern) VALUES (?, ?, ?)", (qty_wheels, flag_color, flag_pattern,))
        con.commit()
        msg = "Record successfully saved"
    except:
      con.rollback()
      msg = "error in update operation"
    finally:
      con.close()
      return render_template("updated.html", msg = msg, violations = violations)

#------------------------------------------------------------
# a page for displaying the buggy
#------------------------------------------------------------
@app.route('/buggy')
def show_buggies():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies")
  records = cur.fetchall(); 
  return render_template("buggy.html", buggies = records)

#------------------------------------------------------------
# a page for edit  the buggy
#------------------------------------------------------------
@app.route('/edit/<buggy_id>')
def edit_buggy(buggy_id):
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=?", (buggy_id,))
  record = cur.fetchone();
  return render_template("buggy-form.html", buggy=record)


#------------------------------------------------------------
# get JSON from current record
#   this is still probably right, but we won't be
#   using it because we'll be dipping diectly into the
#   database
#------------------------------------------------------------
@app.route('/json')
def summary():
  con = sql.connect(DATABASE_FILE)
  con.row_factory = sql.Row
  cur = con.cursor()
  cur.execute("SELECT * FROM buggies WHERE id=? LIMIT 1", (DEFAULT_BUGGY_ID))
  return jsonify(
      {k: v for k, v in dict(zip(
        [column[0] for column in cur.description], cur.fetchone())).items()
        if (v != "" and v is not None)
      }
    )

#------------------------------------------------------------
# delete the buggy
#   don't want DELETE here, because we're anticipating
#   there always being a record to update (because the
#   student needs to change that!)
#------------------------------------------------------------
@app.route('/delete', methods = ['POST'])
def delete_buggy():
  try:
    msg = "deleting buggy"
    with sql.connect(DATABASE_FILE) as con:
      cur = con.cursor()
      cur.execute("DELETE FROM buggies")
      con.commit()
      msg = "Buggy deleted"
  except:
    con.rollback()
    msg = "error in delete operation"
  finally:
    con.close()
    return render_template("updated.html", msg = msg)

@app.route('/poster')
def poster():
   return render_template('poster.html')


if __name__ == '__main__':
   app.run(debug = True, host="0.0.0.0")

          