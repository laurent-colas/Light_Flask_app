import sqlite3
import csv

con = sqlite3.connect('database.db')
print ("Opened database successfully");

c = con.cursor()


def create_db():
    # get the count of tables with the name
    c.execute(''' SELECT count(name) FROM sqlite_master WHERE type='table' AND name='lights' ''')
    # if the count is 1, then table exists
    if c.fetchone()[0] == 1:
        print('Table exists.')
        c.execute('DROP TABLE lights');
    else:
        print('Table does not exist.')

    con.execute('CREATE TABLE lights (addr TEXT, name TEXT, brightness real, eol text)')

def init_db(data):
    for i in range (0,len(data)):
        c.execute("INSERT INTO lights (addr,name,brightness,eol) VALUES(?, ?, ?, ?)", (data[i][0], data[i][1], data[i][2], data[i][3]))
        con.commit()


def read_csv():
    with open('light_db.csv',  encoding="UTF-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',')
        line_count = 0
        data1 = []
        for row in csv_reader:
            print(f'\t adresse: {row[0]} name: {row[1]} bright: {row[2]} eol: {row[3]} ')
            list_temp = [row[0], row[1], row[2], row[3]]
            data1.append(list_temp)
            line_count += 1

        print(f'Processed {line_count} lines.')
        return data1

data = []
data = read_csv()

create_db()
init_db(data)