import sqlite3
import csv
import comm_functions

def create_db():
    con = sqlite3.connect('database.db')
    c = con.cursor()
    # get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='lights' ''')
    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        print('Table exists.')
        c.execute('DROP TABLE lights');
    else:
        print('Table does not exist.')

    con.execute('CREATE TABLE lights (addr TEXT, name TEXT, brightness real, eol text)')

def create_macro_db():
    con = sqlite3.connect('database.db')
    c = con.cursor()
    # get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='macros' ''')
    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        print('Table exists.')
        c.execute('DROP TABLE macros');
    else:
        print('Table does not exist.')

    con.execute('CREATE TABLE macros (name TEXT, brightness REAL, eol TEXT, places TEXT)')

def connect_db():
    con = sqlite3.connect('database.db')
    print("Opened database successfully");
    c = con.cursor()
    return con, c

def init_db(data):
    con = sqlite3.connect('database.db')
    print("Opened database successfully");
    c = con.cursor()
    for i in range (0,len(data)):
        c.execute("INSERT INTO lights (addr,name,brightness,eol) VALUES(?, ?, ?, ?)", (data[i][0], data[i][1], data[i][2], data[i][3]))
        con.commit()

def init_macro_db(data):
    con = sqlite3.connect('database.db')
    print("Opened database successfully");
    c = con.cursor()
    for i in range (0,len(data)):
        c.execute("INSERT INTO macros (name,brightness,eol,places) VALUES(?, ?, ?, ?)", (data[i][0], data[i][1], data[i][2], data[i][3]))
        con.commit()

def read_csv(csv_file_name):
    with open(csv_file_name,  encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        data = []
        for row in csv_reader:
            print(f'\t addr: {row[0]} name: {row[1]} bright: {row[2]} eol: {row[3]} ')
            list_temp = [row[0], row[1], row[2], row[3]]
            data.append(list_temp)
            line_count += 1

        print(f'Processed {line_count} lines.')
        return data

def read_csv_macro(csv_file_name):
    with open(csv_file_name,  encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        data = []
        for row in csv_reader:
            print(f'\t name: {row[0]} bright: {row[1]} eol: {row[2]} lights: {row[3]} ')
            list_temp = [row[0], row[1], row[2], row[3]]
            data.append(list_temp)
            line_count += 1

        print(f'Processed {line_count} lines.')
        return data

def change_light_state(brightness, address):
    try:
        con = sqlite3.connect('database.db')
        c = con.cursor()
        sql_update_query = """Update lights set brightness = ? where addr = ?"""
        data = (brightness, address)
        c.execute(sql_update_query, data)
        con.commit()

        comm_functions.send_light_state(address, brightness)

        confirmation_string = "Update " + address + " to brightness " + brightness
        print(confirmation_string)
        c.close()
    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if (con):
            con.close()
            print("The SQLite connection is closed")

def change_macros_state(brightness, name):
    try:
        con = sqlite3.connect('database.db')
        c = con.cursor()
        sql_update_query = """Update macros set brightness = ? where name = ?"""
        data = (brightness, name)
        c.execute(sql_update_query, data)
        con.commit()
        print("Update " + name + " to brightness " + brightness)

        # get places for macro
        c.execute("SELECT * FROM macros WHERE name=?", (name,))
        rows = c.fetchall()
        if len(rows) == 0:
            print("Macro not found")
        else:
            places = rows[0][3].split(" ")
            for light in places:
                c.execute("UPDATE lights SET brightness= ? WHERE addr= ?", (brightness,light,))
                con.commit()
                comm_functions.send_light_state(light, brightness)
                print("Update " + light + " to brightness " + brightness)
        c.close()
    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if (con):
            con.close()
            print("The SQLite connection is closed")

def update_db():
    data = []
    data = read_csv('light_db.csv')
    create_db()
    init_db(data)

def update_macro_db():
    data = []
    data = read_csv_macro('macro_db.csv')
    create_macro_db()
    init_macro_db(data)

def get_addr_from_name(con, c, name):
    c.execute("SELECT * FROM lights WHERE name=?", (name,))
    rows = c.fetchall()
    address = rows[0][0]
    return address

def add_macro(macro_name, places):
    try:
        con = sqlite3.connect('database.db')
        c = con.cursor()
        places_string = ""
        if type(places) is list:
            for place in places:
                address = get_addr_from_name(con, c, place)
                places_string += address + " "
            places_string = places_string[0:-1]
        else:
            address = get_addr_from_name(con, c, places)
            places_string += address
        c.execute("INSERT INTO macros (name,brightness,eol,places) VALUES(?, ?, ?, ?)",
                  (macro_name, 0, "NA", places_string))
        con.commit()
        print("Macro: " + macro_name + " added to db")
    except sqlite3.Error as error:
        print("Failed to update sqlite table", error)
    finally:
        if (con):
            con.close()
            print("The SQLite connection is closed")

def get_all_places():
    con = sqlite3.connect('database.db')
    c = con.cursor()
    c.execute("SELECT name FROM lights")
    rows = c.fetchall()
    list_places = []
    for i in range(1,len(rows)):
        list_places.append(rows[i][0])
    c.close()
    con.close()
    return list_places

def get_name_macros():
    con = sqlite3.connect('database.db')
    c = con.cursor()
    c.execute("SELECT name FROM macros")
    rows = c.fetchall()
    list_macros = []
    for i in range(1,len(rows)):
        list_macros.append(row[i][0])
    c.close()
    con.close()
    return list_macros

def get_in_db(column_name, table_name):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    command = "SELECT " + column_name + " FROM " + table_name
    c.execute(command)
    rows = c.fetchall()
    list = []
    for i in range(1,len(rows)):
        list.append(rows[i][0])
    c.close()
    con.close()
    return list

def get_all_in_db(table_name):
    con = sqlite3.connect('database.db')
    c = con.cursor()
    command = "SELECT * FROM " + table_name
    c.execute(command)
    rows = c.fetchall()
    list = rows[1:]

    c.close()
    con.close()
    return list
# update_db()
# update_macro_db()

