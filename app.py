import json
from flask import Flask, jsonify, render_template, request
import cx_Oracle
import base64
import firebase_admin
from firebase_admin import firestore
from firebase_admin import credentials
cred = credentials.Certificate("groupchat-86546-firebase-adminsdk-ljacw-517e9f9a1a.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

mail = 0
flag = 0
app = Flask(__name__)
email = "ABCD12@gmail.com"
rec_mail = "kdkd"
try:
    oracle_connection_string = 'system/clarence@localhost:1521/XE'
    connection = cx_Oracle.connect(oracle_connection_string)
    cursor = connection.cursor()
except cx_Oracle.DatabaseError as e:
    error, = e.args
    print("Oracle-Error-Code:", error.code)
    print("Oracle-Error-Message:", error.message)

@app.route("/")
def index():
    return render_template("login.html")
@app.route("/hotel_home_page")
def hotel_home_page():
    return render_template("hotel_home.html")
@app.route("/view_food")
def view_food():
    global mail
    try:
        query = f"SELECT food_name, quantity FROM add_food where email = '{mail}'"
        # Fetch food items from the database
        cursor.execute(query)  # Assuming your table is named 'add_food'
        food_items = cursor.fetchall()
        return render_template('hotel_view.html', food_items=food_items)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Oracle-Error-Code:", error.code)
        print("Oracle-Error-Message:", error.message)


@app.route("/signup_page")
def signup_page():
    return render_template("signup.html")

@app.route("/login_page")
def login_page():
    return render_template("login.html")


@app.route("/login", methods=["POST"])
def login():
    global mail,flag
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]
        category = request.form["category"]
        mail = email
        if category == "donor":
            query = f"select * from  donor where email = '{email}'"
            cursor.execute(query)
            result = cursor.fetchall() 
            print(result)
            if (len(result) == 0):
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)
            if(result[0][1] == email and result[0][2] == password):
                return render_template("hotel_home.html")
            else:
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)
        if category == "receiver":
            query = f"select * from  reciever where email = '{email}'"
            cursor.execute(query)
            result = cursor.fetchall() 
            print(result)
            if (len(result) == 0):
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)
            if(result[0][1] == email and result[0][2] == password):
                flag = 1
                return render_template("rec_home.html")
            else:
                error_message = "Invalid username or password"
                return render_template("login.html", error_message=error_message)


@app.route("/signup", methods=["POST"])
def signup():
    if request.method == "POST":
        # Get data from the form
        name = request.form.get("name")
        email = request.form.get("email")
        password = request.form.get("password")
        role = request.form.get("role")
        phone = request.form.get("phone")
        shop_no = request.form.get("shop")
        area = request.form.get("Area")
        district = request.form.get("district")
        state = request.form.get("state")
        pincode = request.form.get("pincode")

        button_clicked = request.form['button_clicked']
        # Insert each set of data into the database
        if(button_clicked == "btn1"):
            if role == "donor":
                query = f"insert into donor values('{name}','{email}','{password}','{phone}','{role}','{pincode}','{shop_no}','{area}','{district}','{state}')"
                print(query)
                cursor.execute(query)
                connection.commit()
            if role == "receiver":
                query = f"insert into reciever values('{name}','{email}','{password}','{phone}','{role}','{pincode}','{shop_no}','{area}','{district}','{state}')"
                print(query)
                cursor.execute(query)
                connection.commit()
            return render_template("login.html")
        

@app.route("/add_food")
def add_food():
    return render_template("hotel_add_food.html")



@app.route("/submit_form", methods=["POST"])
def submit_form():
    global mail
    if request.method == "POST":
    # Get data from the form
        food_name = request.form.getlist("food-name")
        quantity = request.form.getlist("quantity")
        food_images = request.files.getlist("food-image")  # Get list of uploaded files
        button_clicked = request.form['button_clicked']
        # Insert each set of data into the database
        if(button_clicked == "btn1"):
            for i in range(len(food_name)):
                print(mail) # Check if there are any files uploaded
                query = f"insert into add_food values('{mail}','{food_name[i]}','{quantity[i]}')"
                print(query)
                cursor.execute(query)
                connection.commit()
                print("Completed")
            return render_template("hotel_add_food.html",ans = "submited")



@app.route("/update_food", methods=["POST"])
def update_food():
    global mail
    if request.method == "POST":
        # Get the updated data from the request
        food_id = request.form.get("food_id")
        food_name = request.form.get("food_name")
        quantity = request.form.get("quantity")

        # Update the food item in the database
        try:
            query = f"UPDATE add_food SET food_name = '{food_name}', quantity = '{quantity}'where email = '{mail}' and food_name = '{food_name}' "
            print(query)
            cursor.execute(query)
            connection.commit()
            return "Food item updated successfully", 200
        except Exception as e:
            connection.rollback()
            return str(e), 500 
@app.route("/remove_food", methods=["POST"])
def remove_food():
    global connection, cursor, mail
    if request.method == "POST":
        try:
            data = request.json
            food_name = data.get("food_name")
            print(food_name)
            # Remove the food item from the database
            query = f"DELETE FROM add_food WHERE email = '{mail}' and  food_name = '{food_name}'"
            print(query)
            cursor.execute(query)
            connection.commit()
            print("Done")
            connection.commit()
            return "Food item removed successfully", 200
        except Exception as e:
            connection.rollback()
            return str(e), 500

@app.route("/rec_food")
def rec_food():
    global mail
    try:
        query_receiver = f"SELECT * FROM reciever WHERE email = '{mail}'"
        cursor.execute(query_receiver)
        receiver_details = cursor.fetchone()
        print(receiver_details)
        # Fetch names of donors who have provided food items in the same district as the receiver
        district = receiver_details[8]  
        mail = receiver_details[1]
        print(mail)# Assuming the district column index is 8
        query_donors = f"""
            SELECT distinct d.name, d.phone_number, d.shop_no || ',' || d.area || ',' || d.district || ',' || d.state AS address,d.email
        FROM donor d
        INNER JOIN add_food af ON d.email = af.email
        WHERE d.district = '{district}'
        """
        cursor.execute(query_donors)
        donors_in_district = cursor.fetchall()
        donor_mail = [i[3] for i in donors_in_district]
        food = []
        print(donor_mail)
        for i in donor_mail:
            querry = f"select email,food_name,quantity from add_food where email = '{i}'"
            cursor.execute(querry)
            food.append(cursor.fetchall()) 
        print(food)
        print(donors_in_district)

        return render_template("rec_view.html", donors=donors_in_district,food = food)
    except cx_Oracle.DatabaseError as e:
        error, = e.args
        print("Oracle-Error-Code:", error.code)
        print("Oracle-Error-Message:", error.message)


@app.route('/search_food', methods=['POST'])
def search_food():
    global mail
    if request.method == "POST":
        try:
            # Get search parameters from the request
            shop_name = request.form.get('shopName')
            area = request.form.get('area')
            district = request.form.get('district')
            state = request.form.get('state')
            btn = request.form.get('button_clicked')
            print(state)
            if btn == "btn2":
            # Construct the SQL query based on search parameters
                query_search = f"""
                    SELECT DISTINCT d.name, d.phone_number, d.shop_no || ', ' || d.area || ', ' || d.district || ', ' || d.state AS address, d.email
                    FROM donor d
                    INNER JOIN add_food af ON d.email = af.email
                    WHERE 1=1
                """
                if shop_name != '':
                    query_search += f" AND UPPER(d.name) LIKE UPPER('%{shop_name}%')"
                if area != '':
                    query_search += f" AND UPPER(d.area) LIKE UPPER('%{area}%')"
                if district:
                    query_search += f" AND UPPER(d.district) LIKE UPPER('%{district}%')"
                if state:
                    query_search += f" AND UPPER(d.state) LIKE UPPER('%{state}%')"
                cursor.execute(query_search)
                search_results = cursor.fetchall()
                print(search_results)
                print(query_search)
                donor_mail = [i[3] for i in search_results]
                food = []
                print(donor_mail)
                for i in donor_mail:
                    querry = f"select email,food_name,quantity from add_food where email = '{i}'"
                    cursor.execute(querry)
                    food.append(cursor.fetchall()) 
                print(food)
                return render_template("rec_view.html",donors = search_results,food = food)
        except cx_Oracle.DatabaseError as e:
                error, = e.args
                print("Oracle-Error-Code:", error.code)
                print("Oracle-Error-Message:", error.message)
                return jsonify({"error": "An error occurred while performing the search."})

@app.route("/chatHome", methods=["post", "get"])
def go_to_chatHome():
    global mail,flag
    district_querry = f"SELECT distinct district FROM donor"
    if flag == 1:
        query = f"SELECT name FROM reciever where email = '{mail}'"
    if flag == 0:
        query = f"SELECT name FROM donor where email = '{mail}'"
    print(query)
    cursor.execute(query)  # Assuming your table is named 'add_food'
    user = cursor.fetchall()
    print(user)
    cursor.execute(district_querry)  # Assuming your table is named 'add_food'
    district = cursor.fetchall()
    print(district)
    groups = []
    for i in range(1,len(district)):
        groups.append({"id":f"{district[i][0]}","title":f"{district[i][0]}","description":f"chat for {district[i][0]}","image":"chennai.jpg"})
    return render_template('chat_home.html', groups=groups , user=user)

@app.route('/group_data', methods=['POST'])
def group_data():
    global mail,flag
    district_querry = f"SELECT distinct district FROM donor"
    cursor.execute(district_querry)  # Assuming your table is named 'add_food'
    district = cursor.fetchall()
    groups = []
    for i in range(1,len(district)):
        groups.append({"id":f"{district[i][0]}","title":f"{district[i][0]}","description":f"chat for {district[i][0]}","image":"chennai.jpg"})
    group_id = request.json['group_id']
    group = next((group for group in groups if group['id'] == group_id), None)
    if group:
        name = group['id']
        group_ref = db.collection('Groups').document(name)

        messages_ref = group_ref.collection('messages').order_by('timestamp', direction=firestore.Query.DESCENDING).limit(10)
        messages = messages_ref.stream() 
        message_data = [message.to_dict() for message in messages] 

        d = {
            'g_name' : name,
            'messages' : message_data
        }

        return jsonify(d)
    else:
        return jsonify({'error': 'Group not found'}), 404
    
@app.route('/group_chat')
def group_chat():
    messages_data = request.args.get('messages')
    g_name = request.args.get('group_name')
    user = request.args.get('user')
    print(user)
    messages = json.loads(messages_data)

    return render_template('group_chat.html', messages=messages, g_name=g_name, user=user)

@app.route('/sendMessage', methods=["GET", "POST"])
def sendMessage():
    g_name = request.form['groupName']
    sender = request.form['userName']
    msg = request.form['message']
    print(sender)
    ref = db.collection('Groups').document(g_name)
    messages_ref = ref.collection('messages')

    message = {
        'content' : msg,
        'sender' : sender,
        'timestamp' : firestore.SERVER_TIMESTAMP
    }

    messages_ref.add(message)

    messages = messages_ref.stream() 
    message_data = [message.to_dict() for message in messages] 

    return render_template('group_chat.html', messages=message_data, g_name=g_name, user=sender)

if(__name__ == "__main__"):
    app.run(debug = True)