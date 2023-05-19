from flask import Flask , request ,url_for , render_template,session,redirect,flash
import numpy as np
import pickle
import sqlite3


sc = pickle.load(open('sc.pkl' , 'rb'))

model = pickle.load(open('knnmodel.pkl' , 'rb'))
app = Flask(__name__)

app.secret_key = "hello"



@app.route('/')
def home():
    if 'name' in session:
        session.pop('name', None)
    return render_template("home.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/register')
def register():
    return render_template("register.html")



@app.route("/login_validation", methods=['POST'])
def login_validation():
    email = request.form.get("email")
    password = request.form.get("password")
    flag = 1
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS USER(name text, email text,password text)''')
    conn.commit()
    table = conn.execute("SELECT * FROM USER")
    for row in table:
        print(email + " " + password+" "+row[1]+" "+row[2])
        if email == row[1] and password == row[2]:
            uname = row[0]
            flag = 0
    if flag == 0:
        print(email+" "+password)
        session['name'] = uname
        print(session['name'])
        return redirect(url_for("predict"))
    else:
        flash("Please recheck your credentials")
        return render_template("login.html")


@app.route("/register_validation", methods=['POST'])
def register_validation():
    name = request.form.get("nameR")
    email = request.form.get("emailR")
    password = request.form.get("passwordR")
    specialsym = ['$', '@', '#', '%']
    val = True

    if len(password) < 6:
        flash('Length of password should be at least 6', 'info')
        return render_template("register.html")

    if len(password) > 20:
        flash('Length of password should be not be greater than 20')
        return render_template("register.html")

    if not any(char.isdigit() for char in password):
        flash('Password should have at least one number')
        return render_template("register.html")

    if not any(char.isupper() for char in password):
        flash('Password should have at least one uppercase letter')
        return render_template("register.html")

    if not any(char.islower() for char in password):
        flash('Password should have at least one lowercase letter')
        return render_template("register.html")

    if not any(char in specialsym for char in password):
        flash('Password should have at least one of the symbols $@#')
        return render_template("register.html")

    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS USER(name text, email text,password text)''')
    conn.commit()
    table = conn.execute("SELECT * FROM USER")
    for row in table:
        if row[1] == email:
            flash("You are already registered with this email.Try another")
            return render_template("register.html")

    sql = """INSERT INTO USER (NAME,EMAIL,PASSWORD) VALUES(?,?,?)"""
    cursor = conn.cursor()
    cursor.execute(sql, (name, email, password))
    conn.commit()
    print("Records Created")
    table = conn.execute("SELECT * FROM USER")
    for row in table:
        print(row[0]+" "+row[1]+"\n")
    conn.close()
    flash('Registration successful you can login with your credentials', 'info')
    return render_template("login.html")


@app.route('/predict')
def predict():
    if 'name' in session:
        print("hello")
        return render_template("index.html")
    else:
        flash("Login in inorder to use predict")
        return redirect(url_for("login"))


@app.route('/predict_validation', methods=['POST'])
def predict_validation():
    one = ['yes', 'present', 'good', 'normal', 'Yes', 'Present', 'Good', 'Normal', 'YES', 'PRESENT', 'GOOD', 'NORMAL']
    zero = ['no', 'notpresent', 'not present', 'poor', 'abnormal', 'No', 'Notpresent', 'NotPresent', 'Not Present',
            'Poor', 'Abnormal', 'AbNormal', 'NO', 'NOTPRESENT', 'NOT PRESENT', 'POOR', 'ABNORMAL']
    int_features = []
    # console.log("waiting")
    for i in request.form.values():
        if i in one:
            int_features.append(1.0)
        elif i in zero:
            int_features.append(0.0)
        else:
            int_features.append(float(i))

    final_features = [np.array(int_features)]

    final_features = sc.transform(final_features)
    prediction = model.predict(final_features)[0]

    output = prediction

    if output < 0.5:
        output = 0
    else:
        output = 1
    return render_template('result.html', prediction=output)



# def predict():
#     inputs = [float(x) for x in request.form.values()]
#     inputs = np.array([inputs])
#     inputs = sc.transform(inputs)
#     output = model.predict(inputs)
#     if output < 0.5:
#         output = 0
#     else:
#         output = 1
#     return render_template('result.html' , prediction = output)


@app.route('/result')
def result():
    return render_template("result.html")


@app.route('/logout')
def logout():
    if 'name' in session:
        session.pop('name', None)
        return redirect(url_for("home"))
    else:
        flash("Login in inorder to logout")
        return redirect(url_for("login"))



if __name__ =='__main__':
    app.run(debug=True)