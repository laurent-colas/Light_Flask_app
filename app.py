from __future__ import unicode_literals
from flask import Flask, request, render_template
from flask_wtf import FlaskForm
from flask_thumbnails import Thumbnail

from wtforms import FloatField, StringField
from wtforms.validators import DataRequired
from flask import Flask, render_template, request
import sqlite3 as sql
import threading
import db_functions as db_func


app = Flask(__name__)
app.config['TESTING'] = True
app.config['SECRET_KEY'] = 'you-will-never-guess'

class MacroForm(FlaskForm):
    choices = db_func.get_in_db('name', 'lights')
    macro_new_name = StringField('Name of macro', validators=[DataRequired()])

@app.route('/enternew')
def new_student():
   return render_template('student.html')

@app.route('/enternewmacros')
def new_macro():
    form = MacroForm()
    choices = db_func.get_in_db('name', 'lights')
    return render_template('macros.html', form=form, choices=choices)

@app.route('/addrec', methods=['POST', 'GET'])
def addrec():
    if request.method == 'POST':
        try:
            nm = request.form['nm']
            addr = request.form['add']
            city = request.form['city']
            pin = request.form['pin']

            with sql.connect("database.db") as con:
                cur = con.cursor()
                cur.execute("INSERT INTO students (name,addr,city,pin) VALUES(?, ?, ?, ?)",(nm,addr,city,pin) )

                con.commit()
                msg = "Record successfully added"
        except:
            con.rollback()
            msg = "error in insert operation"

        finally:
            return render_template("result.html", msg=msg)
            con.close()

@app.route('/list')
def list():
    con = sql.connect("database.db")
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from lights")

    rows = cur.fetchall();
    return render_template("list.html", rows=rows)

@app.route('/add_macros', methods=['GET', 'POST'])
def add_macros():
    if request.method == 'POST':
        form = MacroForm()
        choices = db_func.get_all_places()
        macro_names = db_func.get_in_db('name', 'macros')

        new_macro_name = form.macro_new_name.data
        if new_macro_name in macro_names:
            new_macro_name = new_macro_name + "1"
        macro_places = request.form.getlist('room')

        db_func.add_macro(new_macro_name, macro_places)
        rows = db_func.get_all_in_db('macros')
        msg = "Macro successfully added"

        return render_template('macros_button.html', rows=rows, form=form)

@app.route('/macros', methods=['GET', 'POST'])
def macros():
    form = MacroForm()
    if request.method == 'POST':
        macro_name = request.form['submit']
        macro_brightness = request.form[macro_name]
        db_func.change_macros_state(macro_brightness, macro_name)
    rows = db_func.get_all_in_db('macros')
    return render_template('macros_button.html', rows=rows, form=form)

@app.route('/', methods=['GET', 'POST'])
def all_lights():
    form = MacroForm()
    if request.method == 'POST':
        light_name = request.form['submit']
        light_brightness = request.form[light_name]
        db_func.change_light_state(light_brightness, light_name)
    rows = db_func.get_all_in_db('lights')
    return render_template('brightness_button.html', rows=rows, form=form)

if __name__ == '__main__':
    app.run()
