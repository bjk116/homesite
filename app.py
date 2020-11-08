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

@app.route('/')
def index():
    """
    Shows all the possible links to tables using th same dictionary
    to simplify adding a view and if it's viewable.
    """
    links = paramToDBMap.keys()
    print(f"links {links}")
    title = "Apartment 268"
    return render_template("index.html", title=title, links=links)

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
