from flask import Flask, request, render_template
from flask_restful import Api, Resource
import sqlite3

app = Flask(__name__)

def Populate_db():
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()

    cursorObj.execute("DROP TABLE IF EXISTS inventory")
    cursorObj.execute("CREATE TABLE inventory (name TEXT, url TEXT, cost INTEGER, stock INTEGER)")
    cursorObj.execute("INSERT INTO inventory (name, url, cost, stock) VALUES ('shirt', 'static/images/shirt.jpeg', 90, 5), ('Trouser', 'static/images/trouser.jpg', 150, 5), ('Belt', 'static/images/belt.jpg', 45, 5),('Sunglass', 'static/images/glass.jpg', 150, 0)")

    cursorObj.execute("DROP TABLE IF EXISTS transactions")
    cursorObj.execute("CREATE TABLE transactions (time TEXT, id INTEGER, cost INTEGER)")

    con.commit()
    print("database successfully populated")

@app.route("/")
def shop_page():
    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()
    cursorObj.execute("SELECT rowid, * from inventory")

    rows = cursorObj.fetchall()
    print("Receieved %d number of rows", len(rows))

    inventory = []
    for row in rows:
        inventory.append({
            "id" : row[0],
            "name" : row[1],
            "url": row[2],
            "cost" :row[3],
            "stock" : row[4]
        })
    print("id = " + str(inventory[0]["id"]))
    print("name = " + str(inventory[0]["name"] ))
    print("cost =" +  str(inventory[0]["cost"])) 

    
    cursorObj.execute("SELECT SUM(cost) FROM transactions")
    ret = cursorObj.fetchone()[0]
    earnings = ret if ret else 0
    earnings = 1000-earnings
    return render_template("index.html", inventory = inventory, earnings = earnings)

@app.route("/buy/<id>")
def buy(id):
    print("coming here")
    if not id:
        return render_template("message.html", message="Invalid product ID")

    con = sqlite3.connect('mydatabase.db')
    cursorObj = con.cursor()

    cursorObj.execute("SELECT rowid, cost, stock FROM inventory WHERE rowid = ?", (id))
    ret = cursorObj.fetchone()

    if not ret:
        return render_template("message.html", message="Invalid product ID")
    (rowid, cost, stock) = ret

    if stock <=0:
        return render_template("message.html", message="Item out of stock!")

    print("Processed transcation of value %d", cost)
    cursorObj.execute("INSERT INTO transactions (time, id, cost) VALUES (datetime(), ?, ?)", (id, cost))
    cursorObj.execute("UPDATE inventory SET stock = stock - 1 WHERE rowid = ?", (id))
    con.commit()
    return render_template("message.html", message="Purchase Successful")
    
if __name__ == "__main__":
    Populate_db()
    app.run(debug=True)