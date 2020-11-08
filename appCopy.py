from flask import Flask, render_template
import datetime
import mariadb
from flask_bootstrap import Bootstrap

app = Flask(__name__)
Bootstrap(app)

dbConfig = {
        'host':'127.0.0.1', 'port':3306, 'user':'flask',
        'password': 'flask', 'database':'ubuntu'
    }

paramToDBMap = {
         'todos':{'tableName':'dailytodos'},
         'errands':{'tableName':'errands'},
         'dailyTemps':{'tableName':'dailyTemperatures'},
         'templog':{'tableName':'temperature_log'},
         'goals':{'tableName':'goals'},
         'thoughts':{'tableName':'thoughts'},
         'affirm':{'tableName':'affirmations'},
         'scene':{'tableName':'scenario'}
    }

#class DateTimeEncoder(json.JSONEncoder):
#    def default(self, z):
#        if isinstance(z, datetime.datetime):
#             return (str(z))
#        else:
#             return (str(z))
#             return super().default(Z)

@app.route('/')
def index():
    now = datetime.datetime.now()
    timeString = now.strftime("%Y-%m-%d %H:%M")
    templateData = {
        'title' : 'Hello!',
        'time' : timeString
    }
    return render_template('index.html', **templateData)

@app.route('/temp')
def temp():
    conn = mariadb.connect(**dbConfig)
    cur = conn.cursor()
    cur.execute("SELECT id, t_stamp, degrees FROM temperature_log ORDER BY id DESC LIMIT 10")
    row_headers = [x[0] for x in cur.description]
    rv = cur.fetchall()
    json_data=[]
    for result in rv:
        json_data.append(dict(zip(row_headers, str(result))))
    print(rv)
    conn.close()
    return render_template('temp.html', data=rv)

@app.route('/temp/culm')
def temp_culm():
    success = True
    err = None
    try:
        conn = mariadb.connect(**dbConfig)
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT DATE(t_stamp), MIN(degrees), AVG(degrees), MAX(degrees) FROM temperature_log GROUP BY DATE(t_stamp)")
        rv = cur.fetchall()
        print(rv)
    except Exception as e:
        print("Error")
        print(str(e))
        success, err = False, e
    finally:
        conn.close()
    if success:
        return render_template('tempculm.html', data=rv)
    else:
        return render_template('error.html', error=err)

@app.route('/errands')
def errrands():
    success = True
    err = None
    try:
        conn = mariadb.connect(**dbConfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM errands")
        rv = cursor.fetchall()
        print(rv)
    except Exception as e:
        print("error")
        print(str(e))
        success = False
        err = e
    finally:
        conn.close()
    if success:
        return render_template('errands.html', data = rv)
    else:
        return render_template('error.html', error=err)

@app.route('/')
def tableOfContents():
    """
    Shows all the possible links to tables using th same dictionary
    to simplify adding a view and if it's viewable.
    """
    links = paramToDBMap.keys()
    print(f"links {links}")
    title = "Navigation"
    return render_template("navigation.html", title=title, links=links)

@app.route('/view/<string:tablename>')
@app.route('/view/<string:tablename>/<int:limit>')
def viewTable(tablename=None, limit=100):
    """This should only be allowed to viewed by admin users
    since it's kind of dangerous to leave this open to the
    general user"""
    if not tablename:
        return render_template('error.html', error="Format is //table//tablename//limit where limit is option")
    success = True
    err = None
    try:
        dbTable = paramToDBMap[tablename]['tableName']
        conn = mariadb.connect(**dbConfig)
        cursor = conn.cursor()
        query = f"SELECT * FROM {dbTable} LIMIT {limit}"
        print(query)
        cursor.execute(query)
        row_headers = [x[0] for x in cursor.description]
        print(f"row headers {row_headers}")
        rv = cursor.fetchall()
        print(rv)
    except KeyError:
        return render_template("error.html", error="Table does not exist")
    except Exception as e:
        print("error")
        print(str(e))
        success = False
        err = e
    finally:
        conn.close()
    if success:
        print(f"title: {dbTable}")
        print(f"header: {row_headers}")
        return render_template('tableview.html', title=dbTable, headers=row_headers, data = rv)
    else:
        return render_template('error.html', error = err)

@app.route('/todos')
def todos():
    success = True
    err = None
    try:
        conn = mariadb.connect(**dbConfig)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM dailytodos")
        rv = cursor.fetchall()
        print(rv)
    except Exception as e:
        print("error")
        print(str(e))
        err = e
        success = False
    finally:
        conn.close()
    if success:
        return render_template('todos.html', data = rv)
    else:
        return render_template('errors.html', error=err)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
