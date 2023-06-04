from flask import Flask, render_template, request, flash, redirect, url_for, abort, request, session
from flask_mysqldb import MySQL
# initially created by __init__.py, need to be used here
from librarydb import app, db

from librarydb.forms import Users_form, School_form, Borrows_form, Reservations_form, Reviews_form, Books_form
global role


@app.route("/")
def index():
    try:
        global role

        return render_template("start.html", pageTitle="Welcome!")
    except Exception as e:
        print(e)
        return render_template("start.html", pageTitle="Welcome!")


@app.route("/login", methods=['GET', 'POST'])
def login():

    if request.method == 'POST':
        type2 = request.form['type'].lower()
        if type2 == 'admin':
            session['role'] = 1

            cur = db.connection.cursor()
            cur.execute(
                "SELECT Users.Username, Users.Password FROM Users INNER JOIN Administrator Ad ON Users.User_id = Ad.User_id;")
            column_names = [i[0] for i in cur.description]
            users = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()

            username_global = request.form['username']
            password = request.form['password']

            if any(user['Username'] == username_global and user['Password'] == password for user in users):
                session['username'] = username_global  # Store the username in the session
                return render_template("landing1.html", pageTitle="Welcome, Administrator!", username=username_global)
            else:
                flash("Invalid username or password", "error")
                return render_template("start.html", pageTitle="Welcome!")

        elif type2 == 'operator':
            session['role'] = 2

            cur = db.connection.cursor()
            cur.execute(
                "SELECT Users.Username, Users.Password FROM Users INNER JOIN School_Lib_Op Op ON Users.User_id = Op.User_id;")
            column_names = [i[0] for i in cur.description]
            users = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()

            username_global = request.form['username']
            password = request.form['password']

            if any(user['Username'] == username_global and user['Password'] == password for user in users):
                session['username'] = username_global  # Store the username in the session
                return render_template("landing2.html", pageTitle="Welcome, Operator!", username=username_global)
            else:
                flash("Invalid username or password", "error")
                return render_template("start.html", pageTitle="Welcome!")

        elif type2 == 'user':

            cur = db.connection.cursor()
            cur.execute(
                "SELECT Users.Username, Users.Password, USA.Type FROM Users INNER JOIN Basic_Users USA ON Users.User_id = USA.User_id;")
            column_names = [i[0] for i in cur.description]
            users = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()

            username_global = request.form['username']
            password = request.form['password']
            
            if any(user['Username'] == username_global and user['Password'] == password for user in users):
                for user in users:
                    if user['Username'] == username_global and user['Password'] == password:
                        if user['Type'] == 'Teacher':
                            session['role'] = 3
                        else:
                            session['role'] = 4
                        session['username'] = username_global  # Store the username in the session
                        return render_template("landing3.html", pageTitle="Welcome, User!", username=username_global)
            else:
                flash("Invalid username or password", "error")
                return render_template("start.html", pageTitle="Welcome!")
        else:
            return render_template("start.html", pageTitle="Welcome!")


@app.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear()  # Clear the session
    return redirect(url_for('index'))


@app.route("/landing")
def landing():
    if 'role' in session:
        role = session['role']
        if role == 1:
            return redirect(url_for('landing_admin'))
        elif role == 2:
            return redirect(url_for('landing_operator'))
        elif role == 3 or role == 4:
            return redirect(url_for('landing_user'))
        else:
            return redirect(url_for('index'))
    else:
        return redirect(url_for('index'))


@app.route("/landing/admin")
def landing_admin():
    return render_template("landing1.html", pageTitle="Welcome, Administrator!", username = session['username'])


@app.route("/landing/operator")
def landing_operator():
    return render_template("landing2.html", pageTitle="Welcome, Operator!", username = session['username'])


@app.route("/landing/user")
def landing_user():
    return render_template("landing3.html", pageTitle="Welcome, User!", username = session['username'])


@app.route("/myUser/<string:Username>")
def getmyUser(Username):
    """
    Retrieve Users from database
    """
    try:
        form = Users_form()
        cur = db.connection.cursor()
        cur.execute(
            f"Select U.*, CASE  WHEN BU.Type is not null THEN BU.Type WHEN Op.User_id IS not NULL THEN 'Operator' ELSE 'Administrator' END AS Type, CASE WHEN BU.School_id is not null THEN BU.School_id WHEN OP.School_id is not null Then OP.School_id ELSE NUll END AS School_id FROM Users U LEFT JOIN Basic_Users BU ON U.User_id=BU.User_id LEFT JOIN School_Lib_Op Op ON U.User_id = OP.User_id WHERE U.Username = '{Username}';")
        column_names = [i[0] for i in cur.description]
        Users = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        return render_template("myUser.html", Users=Users, pageTitle="My User", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/myUser/update/<string:Username>", methods=["POST"])
def updatemyUser(Username):
    form = Users_form()  # see createUsers for explanation
    updateData = form.__dict__
    if (form.validate_on_submit()):

        query = "UPDATE Users SET Username = '{}', Password = '{}', Date_of_birth = '{}', Full_name = '{}', Email = '{}' WHERE Username = '{}';".format(
            updateData['Username'].data, updateData['Password'].data, updateData['Date_of_birth'].data, updateData['Full_name'].data, updateData['Email'].data, Username)

        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            session['username'] = Username
            return redirect(url_for('index'))
        
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
        return redirect(url_for('updatemyUser',username = Username))


@app.route("/myUser/delete/<string:Username>", methods=["POST"])
def deletemyUser(Username):
    query = f"DELETE FROM Users WHERE Username = '{Username}';"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        # flash("User deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for('index'))
    # return redirect(url_for("getmyUser", Username=Username))


@app.route("/Users")
def getUsers():
    """
    Retrieve Users from database
    """
    try:
        form = Users_form()
        cur = db.connection.cursor()
        cur.execute("Select U.*, CASE  WHEN BU.Type is not null THEN BU.Type WHEN Op.User_id IS not NULL THEN 'Operator' ELSE 'Administrator' END AS Type, CASE WHEN BU.School_id is not null THEN BU.School_id WHEN OP.School_id is not null Then OP.School_id ELSE NUll END AS School_id FROM Users U LEFT JOIN Basic_Users BU ON U.User_id=BU.User_id LEFT JOIN School_Lib_Op Op ON U.User_id = OP.User_id;")
        column_names = [i[0] for i in cur.description]
        Users = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        return render_template("Users.html", Users=Users, pageTitle="Users Page", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/Users/create", methods=["GET", "POST"])
def createUsers():
    """
    Create new User in the database
    """
    form = Users_form()

    # when the form is submitted
    if request.method == "POST" and form.validate_on_submit():
        newUser = form.__dict__
        query = "INSERT INTO Users(Username, Password, Date_of_birth, Full_name, Email) VALUES ('{}', '{}', '{}', '{}', '{}');".format(
            newUser['Username'].data, newUser['Password'].data, newUser['Date_of_birth'].data, newUser['Full_name'].data, newUser['Email'].data)

        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()

            # Get the last inserted User_id
            cur = db.connection.cursor()
            cur.execute("SELECT LAST_INSERT_ID();")
            user_id = cur.fetchone()[0]
            cur.close()

            if newUser['Type'].data == 'Administrator':
                query2 = "INSERT INTO Administrator(User_id) VALUES ({});".format(
                    user_id)
                cur = db.connection.cursor()
                cur.execute(query2)
                db.connection.commit()
                cur.close()
            elif newUser['Type'].data == 'Operator':
                query2 = "INSERT INTO School_Lib_Op(User_id, School_id) VALUES ({}, '{}');".format(
                    user_id, newUser['School_id'].data)
                cur = db.connection.cursor()
                cur.execute(query2)
                db.connection.commit()
                cur.close()
            elif newUser['Type'].data == 'Teacher' or newUser['Type'].data == 'Student':
                query2 = "INSERT INTO Basic_Users(User_id, School_id, Type) VALUES ({}, '{}', '{}');".format(
                    user_id, newUser['School_id'].data, newUser['Type'].data)
                cur = db.connection.cursor()
                cur.execute(query2)
                db.connection.commit()
                cur.close()

            flash("User inserted successfully :)", "success")
            return redirect(url_for('landing'))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("create_Users.html", pageTitle="Insert User", form=form)


@app.route("/Users/update/<int:UsersID>", methods=["POST"])
def updateUsers(UsersID):
    """
    Update a User in the database, by id
    """
    form = Users_form()  # see createUsers for explanation
    updateData = form.__dict__
    if (form.validate_on_submit()):
        query = "UPDATE Users SET Username = '{}', Password = '{}', Date_of_birth = '{}', Full_name = '{}', Email = '{}' WHERE User_id = {};".format(
            updateData['Username'].data, updateData['Password'].data, updateData['Date_of_birth'].data, updateData['Full_name'].data, updateData['Email'].data, UsersID)

        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()

            if updateData['Type'].data == 'Operator':
                query2 = "UPDATE School_Lib_Op SET School_id ='{}' WHERE User_id = {});".format(
                    updateData['School_id'].data, UsersID)
                cur = db.connection.cursor()
                cur.execute(query2)
                db.connection.commit()
                cur.close()
            elif updateData['Type'].data == 'Teacher' or updateData['Type'].data == 'Student':
                query2 = "UPDATE Basic_Users SET School_id ='{}' WHERE User_id =  {};".format(
                    updateData['School_id'].data, UsersID)

                cur = db.connection.cursor()
                cur.execute(query2)
                db.connection.commit()
                cur.close()

            flash("User updated successfully", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
    return redirect(url_for("getUsers"))


@app.route("/Users/delete/<int:UsersID>", methods=["POST"])
def deleteUsers(UsersID):
    """
    Delete User by id from database
    """
    query = f"DELETE FROM Users WHERE User_id = {UsersID};"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("User deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("getUsers"))


@app.route("/School_Dep")
def getSchool():
    """
    Retrieve Schools from database
    """
    try:
        form = School_form()
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM School_Dep")
        column_names = [i[0] for i in cur.description]
        School_Dep = [dict(zip(column_names, entry))
                      for entry in cur.fetchall()]
        cur.close()
        return render_template("School_Dep.html", School_Dep=School_Dep, pageTitle="Insert User", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/School_Dep/create", methods=["GET", "POST"])  # "GET" by default
def createSchool():
    """
    Create new School in the database
    """
    form = School_form()  # This is an object of a class that inherits FlaskForm

    # when the form is submitted
    if (request.method == "POST" and form.validate_on_submit()):
        newSchool = form.__dict__
        query = "INSERT INTO School_Dep(Address, City, Phone_number, Email, Director_name) VALUES ('{}', '{}', '{}', '{}','{}');".format(
            newSchool['Address'].data, newSchool['City'].data, newSchool['Phone_number'].data, newSchool['Email'].data, newSchool['Director_name'].data)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("School Department inserted successfully :)", "success")
            return redirect(url_for('getSchool'))
        except Exception as e:  # OperationalError
            flash(str(e), "danger")

    # else, response for GET request
    return render_template("create_School_Dep.html", pageTitle="Insert School Dep", form=form)


@app.route("/School_Dep/update/<int:SchoolID>", methods=["POST"])
def updateSchool(SchoolID):
    """
    Update a School in the database, by id
    """
    form = School_form()  # see createUsers for explanation
    updateData = form.__dict__
    if (form.validate_on_submit()):
        query = "UPDATE School_Dep SET Address = '{}', City = '{}', Phone_number = '{}', Email = '{}', Director_name = '{}' WHERE School_id = {};".format(
            updateData['Address'].data, updateData['City'].data, updateData['Phone_number'].data, updateData['Email'].data, updateData['Director_name'].data, SchoolID)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("School Department updated successfully", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
    return redirect(url_for("getSchool"))


@app.route("/School_Dep/delete/<int:SchoolID>", methods=["POST"])
def deleteSchool(SchoolID):
    """
    Delete User by id from database
    """
    query = f"DELETE FROM School_Dep WHERE School_id = {SchoolID};"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("School Department deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("getSchool"))


@app.route("/myBorrows/<string:Username>")
def getmyBorrows(Username):
    """
    Retrieve Borrows from database
    """
    try:
        # form = Borrows_form()
        cur = db.connection.cursor()
        cur.execute(
            f"SELECT B.* FROM BORROWS B INNER JOIN USERS U ON U.User_id = B.User_id WHERE U.Username = '{Username}';")
        column_names = [i[0] for i in cur.description]
        Borrows = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        return render_template("myBorrows.html", Borrows=Borrows, pageTitle="My Borrows")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/Borrows")
def getBorrows():
    """
    Retrieve Schools from database
    """
    try:
        form = Borrows_form()
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM Borrows")
        column_names = [i[0] for i in cur.description]
        Borrows = [dict(zip(column_names, entry))
                   for entry in cur.fetchall()]
        cur.close()
        return render_template("Borrows.html", Borrows=Borrows, pageTitle="Insert Borrow", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/Borrows/create", methods=["GET", "POST"])  # "GET" by default
def createBorrows():
    """
    Create new School in the database
    """
    form = Borrows_form()  # This is an object of a class that inherits FlaskForm

    # when the form is submitted
    if (request.method == "POST" and form.validate_on_submit()):
        newBorrows = form.__dict__
        query = "INSERT INTO Borrows(User_id, Book_id) VALUES ('{}', '{}');".format(
            newBorrows['User_id'].data, newBorrows['Book_id'].data)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Borrow inserted successfully :)", "success")
            return redirect(url_for("createBorrows"))
        except Exception as e:  # OperationalError
            flash(str(e), "danger")

    # else, response for GET request
    return render_template("create_Borrows.html", pageTitle="Insert Borrow", form=form)


@app.route("/Borrows/update/<int:BorrowID>", methods=["POST"])
def updateBorrows(BorrowID):
    """
    Update a School in the database, by id
    """
    form = Borrows_form()  # see createUsers for explanation
    updateData = form.__dict__
    if (form.validate_on_submit()):
        query = "UPDATE Borrows SET Borrow_date = '{}', Return_date = '{}', User_id = '{}', Book_id = '{}'  WHERE Borrow_id = {};".format(
            updateData['Borrow_date'].data, updateData['Return_date'].data, updateData['User_id'].data, updateData['Book_id'].data, BorrowID)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Borrow updated successfully", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
    return redirect(url_for("getBorrows"))


@app.route("/Borrows/delete/<int:BorrowID>", methods=["POST"])
def deleteBorrows(BorrowID):
    """
    Delete User by id from database
    """
    query = f"DELETE FROM Borrows WHERE Borrow_id = {BorrowID};"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("Borrow deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("getBorrows"))


@app.route("/Reservations")
def getReservations():
    """
    Retrieve Schools from database
    """
    try:
        form = Reservations_form()
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM Reservations")
        column_names = [i[0] for i in cur.description]
        Reservations = [dict(zip(column_names, entry))
                        for entry in cur.fetchall()]
        cur.close()
        return render_template("Reservations.html", Reservations=Reservations, pageTitle="Reservations", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/Reservations/create", methods=["GET", "POST"])  # "GET" by default
def createReservations():
    """
    Create new School in the database
    """
    form = Reservations_form()  # This is an object of a class that inherits FlaskForm

    # when the form is submitted
    if (request.method == "POST" and form.validate_on_submit()):
        newReservations = form.__dict__
        query = "INSERT INTO Reservations(User_id, Book_id) VALUES ('{}', '{}');".format(
            newReservations['User_id'].data, newReservations['Book_id'].data)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Reservation inserted successfully :)", "success")
            return redirect(url_for("getReservations"))
        except Exception as e:  # OperationalError
            flash(str(e), "danger")

    # else, response for GET request
    return render_template("create_Reservations.html", pageTitle="Insert Reservation", form=form)


@app.route("/Reservations/update/<int:ReservationID>", methods=["POST"])
def updateReservations(ReservationID):
    """
    Update a Rservation in the database, by id
    """
    form = Reservations_form()
    updateData = form.__dict__
    if (form.validate_on_submit()):
        if updateData['Pickup_date'].data is None:
            query = "UPDATE Reservations SET User_id = '{}', Book_id = '{}', Reservation_date = '{}', Status = '{}' WHERE Reservation_id = {};".format(
                updateData['User_id'].data, updateData['Book_id'].data, updateData['Reservation_date'].data, updateData['Status'].data, ReservationID)
        else:
            query = "UPDATE Reservations SET User_id = '{}', Book_id = '{}', Reservation_date = '{}', Pickup_date = '{}', Status = '{}' WHERE Reservation_id = {};".format(
                updateData['User_id'].data, updateData['Book_id'].data, updateData['Reservation_date'].data, updateData['Pickup_date'].data, updateData['Status'].data, ReservationID)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Reservation updated successfully", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
    return redirect(url_for("getReservations"))


@app.route("/Reservations/delete/<int:ReservationID>", methods=["POST"])
def deleteReservations(ReservationID):
    """
    Delete User by id from database
    """
    query = f"DELETE FROM Reservations WHERE Reservation_id = {ReservationID};"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("Reservation deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("getReservations"))


@app.route("/myReservations/<string:Username>")
def getmyReservations(Username):
    """
    Retrieve Schools from database
    """
    try:
        form = Reservations_form()
        cur = db.connection.cursor()
        cur.execute(
            f"SELECT B.* FROM RESERVATIONS B INNER JOIN USERS U ON U.User_id = B.User_id WHERE U.Username = '{Username}';")
        column_names = [i[0] for i in cur.description]
        Reservations = [dict(zip(column_names, entry))
                        for entry in cur.fetchall()]
        cur.close()
        return render_template("myReservations.html", Reservations=Reservations, pageTitle="my Reservations", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


# "GET" by default
@app.route("/myReservations/create/<string:Username>", methods=["GET", "POST"])
def createmyReservations(Username):
    """
    Create new School in the database
    """
    form = Reservations_form()  # This is an object of a class that inherits FlaskForm

    # when the form is submitted
    if (request.method == "POST"):
        newmyReservations = form.__dict__
        query = "INSERT INTO Reservations(User_id, Book_id) VALUES ((SELECT User_id FROM Users WHERE Username = '{}'),'{}');".format(
            Username, newmyReservations['Book_id'].data)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Reservation inserted successfully :)", "success")
            return redirect(url_for('landing'))
        except Exception as e:  # OperationalError
            flash(str(e), "danger")

    # else, response for GET request
    return render_template("create_myReservations.html", pageTitle="Insert Reservation", form=form)

@app.route("/newReservations")
def getnewReservations():
    """
    Retrieve new Reservations from database
    """
    try:
        form = Reservations_form()
        cur = db.connection.cursor()
        cur.execute("SELECT T2.Reservation_id, T2.Reservation_date, T2.User_id, T2.Book_id, T2.B_Status, T.Type, T.C, T2.R_Status FROM (SELECT R.User_id, U.Type, COUNT(Reservation_id) C FROM Reservations R INNER JOIN Book_copies BC ON R.Book_id = BC.Book_id INNER JOIN Basic_Users U ON U.User_id = R.User_id WHERE datediff(Current_date,Reservation_date) < 7 AND R.Status = 'PENDING' Group BY User_id) AS T INNER JOIN (SELECT User_id, COUNT(Reservation_id), Reservation_id, Reservation_date, BC.Status B_Status, R.Status R_Status, BC.Book_id FROM Reservations R INNER JOIN Book_copies BC ON R.Book_id = BC.Book_id WHERE datediff(Current_date,Reservation_date) < 7 AND R.Status = 'PENDING' Group BY Reservation_id) AS T2 ON T.User_id = T2.User_id;")
        column_names = [i[0] for i in cur.description]
        Reservations = [dict(zip(column_names, entry))
                        for entry in cur.fetchall()]
        cur.close()
        return render_template("new_Reservations.html", Reservations=Reservations, pageTitle="Reservations", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)

@app.route("/newReservations/update/<int:ReservationID>", methods=["POST"])
def updatenewReservations(ReservationID):
    """
    Update a Rservation in the database, by id
    """
    form = Reservations_form()
    updateData = form.dict
    if (form.validate_on_submit()):

        query = "UPDATE Reservations SET User_id = '{}', Book_id = '{}', Status = '{}' WHERE Reservation_id = {};".format(
            updateData['User_id'].data, updateData['Book_id'].data, updateData['Status'].data, ReservationID)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Reservation updated successfully", "success")
            return redirect(url_for('getnewReservations'))
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
        return redirect(url_for('landing'))

@app.route("/Reviews")
def getReviews():
    """
    Retrieve Schools from database
    """
    try:
        form = Reviews_form()
        cur = db.connection.cursor()
        cur.execute("SELECT * FROM Reviews")
        column_names = [i[0] for i in cur.description]
        Reviews = [dict(zip(column_names, entry))
                   for entry in cur.fetchall()]
        cur.close()
        return render_template("Reviews.html", Reviews=Reviews, pageTitle="Insert Review", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)

@app.route("/newReviews")
def getnewReviews():
    """
    Retrieve  from database
    """
    try:
        form = Reviews_form()
        cur = db.connection.cursor()
        cur.execute("SELECT *FROM REVIEWS WHERE Status = 'PENDING';")
        column_names = [i[0] for i in cur.description]
        Reviews = [dict(zip(column_names, entry))
                   for entry in cur.fetchall()]
        cur.close()
        return render_template("Reviews.html", Reviews=Reviews, pageTitle="See pending Reviews", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)

@app.route("/Reviews/create", methods=["GET", "POST"])  # "GET" by default
def createReviews():
    """
    Create new School in the database
    """
    form = Reviews_form()  # This is an object of a class that inherits FlaskForm

    # when the form is submitted
    if (request.method == "POST"):
        newReviews = form.__dict__
        cur = db.connection.cursor()
        cur.execute("SELECT Title FROM Books WHERE ISBN = '{}';".format(newReviews['ISBN'].data))
        result2 = cur.fetchone()
        cur.close()

        if result2 is None:
            flash("ISBN does not exist")
            return render_template("create_Reviews.html", pageTitle="Insert your Review", form=form)
        
        query = "INSERT INTO Reviews(ISBN, User_id, Score, Text) VALUES ('{}', '{}', '{}', '{}');".format(
            newReviews['ISBN'].data, newReviews['User_id'].data, newReviews['Score'].data, newReviews['Text'].data)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Review inserted successfully :)", "success")
            return redirect(url_for("createReviews"))
        except Exception as e:  # OperationalError
            flash(str(e), "danger")

    # else, response for GET request
    return render_template("create_Reviews.html", pageTitle="Insert Review", form=form)


@app.route("/Reviews/update/<int:ReviewID>", methods=["POST"])
def updateReviews(ReviewID):
    """
    Update a Rservation in the database, by id
    """
    form = Reviews_form()
    updateData = form.__dict__
    
    query = "UPDATE Reviews SET Status = '{}' WHERE Review_id = {};".format(updateData['Status'].data, ReviewID)
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("Review updated successfully", "success")
    except Exception as e:
        flash(str(e), "danger")

    return redirect(url_for("getReviews"))


@app.route("/Reviews/delete/<int:ReviewID>", methods=["POST"])
def deleteReviews(ReviewID):
    """
    Delete User by id from database
    """
    query = f"DELETE  FROM Reviews WHERE Review_id = {ReviewID};"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("Review deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("getReviews"))


@app.route("/myReviews/<string:Username>")
def getmyReviews(Username):
    """
    Retrieve myReviews from database
    """
    try:
        form = Reviews_form()
        cur = db.connection.cursor()
        cur.execute(
            f"SELECT R.* FROM Reviews R INNER JOIN Users U ON U.User_id = R.User_id WHERE Username = '{Username}';")
        column_names = [i[0] for i in cur.description]
        myReviews = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()
        return render_template("myReviews.html", myReviews=myReviews, pageTitle="My Reviews", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/myReviews/create/<string:Username>", methods=["GET", "POST"])
def createmyReviews(Username):
    form = Reviews_form()

    if request.method == "POST":
        newmyReviews = form.__dict__

        # Find the User_id based on the Username
        cur = db.connection.cursor()
        cur.execute(f"SELECT User_id FROM Users WHERE Username = '{Username}';")
        result1 = cur.fetchone()
        cur.close()

        cur = db.connection.cursor()
        cur.execute("SELECT Title FROM Books WHERE ISBN = '{}';".format(newmyReviews['ISBN'].data))
        result2 = cur.fetchone()
        cur.close()

        if result2 is None:
            flash("ISBN does not exist")
            return render_template("create_myReviews.html", pageTitle="Insert your Review", form=form)

        if result1 is not None:
            User_id = result1[0]

            query = "INSERT INTO Reviews(ISBN, User_id, Score, Text) VALUES ('{}', '{}', '{}', '{}');".format(
                newmyReviews['ISBN'].data, User_id, newmyReviews['Score'].data, newmyReviews['Text'].data)

            try:
                cur = db.connection.cursor()
                cur.execute(query)
                db.connection.commit()
                cur.close()
                flash("Review inserted successfully :)", "success")
                return redirect(url_for('landing'))
            except Exception as e:
                flash(str(e), "danger")
        else:
            flash("User not found", "danger")

    elif request.method == "GET":

        return render_template("create_myReviews.html", pageTitle="Insert your Review", form=form)
    
    else: 
        flash("Wrong data format", "fail")
        return render_template("create_myReviews.html", pageTitle="Insert your Review", form=form)


@app.route("/myReviews/update/<int:ReviewID>", methods=["POST"])
def updatemyReviews(ReviewID):
    """
    Update a Rservation in the database, by id
    """
    form = Reviews_form()
    updateData = form.__dict__
    if (form.validate_on_submit()):
        query = "UPDATE Reviews SET ISBN = '{}', Score = '{}', Text = '{}' WHERE Review_id = '{}';".format(
            updateData['ISBN'].data, updateData['Score'].data, updateData['Text'].data, ReviewID)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()
            cur.close()
            flash("Review updated successfully", "success")
        except Exception as e:
            flash(str(e), "danger")
    else:
        for category in form.errors.values():
            for error in category:
                flash(error, "danger")
    return redirect(url_for('index'))
    # return redirect(url_for("getmyReviews", Username=Username))


@app.route("/myReviews/delete/<int:ReviewID>", methods=["POST"])
def deletemyReviews(ReviewID):
    """
    Delete User by id from database
    """
    query = f"DELETE FROM Reviews WHERE Review_id = '{ReviewID}';"
    try:
        cur = db.connection.cursor()
        cur.execute(query)
        db.connection.commit()
        cur.close()
        flash("Review deleted successfully", "primary")
    except Exception as e:
        flash(str(e), "danger")
    return redirect(url_for("getmyReviews", Username=session['username']))


@app.route("/Books", methods=["GET", "POST"])
def getBooks():
    if (request.method == 'POST'):
        if (request.form['type'].lower() != 'any'):
            type2 = request.form['type'].lower()
            data = request.form['data']
            if type2 == 'title':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) as 'Authors', GROUP_CONCAT(DISTINCT Category_name) as 'Categories', (SELECT CAST(AVG(Score)AS DECIMAL (3,2))FROM Reviews WHERE ISBN = BC.ISBN) AS Score, GROUP_CONCAT(DISTINCT Book_id) as 'IDs', BC.Library_id Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN WHERE B.Title = '{data}' Group by ISBN,Lib;")
                column_names = [i[0] for i in cur.description]

            elif type2 == 'author':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Category_name) as 'Categories', CASE WHEN Au2 IS NULL THEN Au1 ELSE CONCAT(Au1,', ',Au2) END AS 'Authors', (SELECT CAST(AVG(Score)AS DECIMAL (3,2))FROM Reviews WHERE ISBN = BC.ISBN) AS Score, GROUP_CONCAT(DISTINCT Book_id) as 'IDs', BC.Library_id as 'Library' FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN (SELECT ISBN,Author_name Au1 FROM Authors WHERE Author_name = '{data}') C1 ON C1.ISBN = BC.ISBN LEFT JOIN (SELECT ISBN,Author_name Au2 FROM Authors WHERE Author_name != '{data}') C2 ON C2.ISBN = BC.ISBN INNER JOIN Categories A ON A.ISBN = BC.ISBN GROUP BY ISBN,Library;")
                column_names = [i[0] for i in cur.description]

            elif type2 == 'category':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) as 'Authors', CASE WHEN Cat2 IS NULL THEN Cat1 ELSE CONCAT(CAT1,', ',CAT2) END AS 'Categories', (SELECT CAST(AVG(Score)AS DECIMAL (3,2))FROM Reviews WHERE ISBN = BC.ISBN) AS Score, GROUP_CONCAT(DISTINCT Book_id) as 'IDs', BC.Library_id as 'Library' FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN (SELECT ISBN,Category_name Cat1 FROM Categories WHERE Category_name = '{data}') C1 ON C1.ISBN = BC.ISBN LEFT JOIN (SELECT ISBN,Category_name Cat2 FROM Categories WHERE Category_name != '{data}') C2 ON C2.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = BC.ISBN GROUP BY ISBN,Library;")
                column_names = [i[0] for i in cur.description]

            Books = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()
            return render_template("Books.html", Books=Books, pageTitle="Search Books")
        else:
            cur = db.connection.cursor()
            cur.execute("SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) as 'Authors', GROUP_CONCAT(DISTINCT Category_name) as 'Categories', (SELECT CAST(AVG(Score)AS DECIMAL (3,2))FROM Reviews WHERE ISBN = BC.ISBN) AS Score, GROUP_CONCAT(DISTINCT Book_id) as 'IDs', BC.Library_id Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN Group by ISBN,Lib;")
            column_names = [i[0] for i in cur.description]
            Books = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()
            return render_template("Books.html", Books=Books, pageTitle="Search Books")
    else:
        return redirect(url_for('index'))


@app.route("/Books_init", methods=["GET", "POST"])
def getBooks_init():
    try:
        form = Books_form()
        cur = db.connection.cursor()
        cur.execute(
            "SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) as 'Authors', GROUP_CONCAT(DISTINCT Category_name) as 'Categories', (SELECT CAST(AVG(Score)AS DECIMAL (3,2))FROM Reviews WHERE ISBN = BC.ISBN) AS Score, GROUP_CONCAT(DISTINCT Book_id) as 'IDs', BC.Library_id Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN Group by ISBN,Lib;")
        column_names = [i[0] for i in cur.description]
        Books = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()
        return render_template("Books.html", Books=Books, pageTitle="Books", form=form)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)

    return render_template("Books.html", Books=Books, pageTitle="Search Books")


@app.route("/Books1/create", methods=["GET", "POST"])
def createBooks():
    """
    Create new Book in the database
    """
    form = Books_form()

    # when the form is submitted
    if request.method == "POST" and form.validate_on_submit():
        newBook = form.__dict__
        query = "INSERT INTO Books(ISBN, Library_id, Title, Publisher, Publication_date, Page_count, Summary, Image, Language, Keywords, Total_copies, Available_copies) VALUES ('{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}', '{}');".format(
            newBook['ISBN'].data, newBook['Library_id'].data, newBook['Title'].data, newBook['Publisher'].data, newBook['Publication_date'].data, newBook['Page_count'].data, newBook['Summary'].data, newBook['Image'].data, newBook['Language'].data, newBook['Keywords'].data, newBook['Total_copies'].data, newBook['Total_copies'].data)
        query1 = "INSERT INTO Authors(ISBN, Author_name) VALUES ('{}','{}');".format(
            newBook['ISBN'].data, newBook['Author1'].data)
        query4 = "INSERT INTO Categories(ISBN, Category_name) VALUES ('{}','{}');".format(
            newBook['ISBN'].data, newBook['Category1'].data)
        try:
            cur = db.connection.cursor()
            cur.execute(query)
            db.connection.commit()

            cur.execute(query1)
            db.connection.commit()

            cur.execute(query4)
            db.connection.commit()

            if newBook['Author2'].data:
                query2 = "INSERT INTO Authors(ISBN, Author_name) VALUES ('{}','{}');".format(
                    newBook['ISBN'].data, newBook['Author2'].data)
                cur.execute(query2)
                db.connection.commit()

            if newBook['Author3'].data:
                query3 = "INSERT INTO Authors(ISBN, Author_name) VALUES ('{}','{}');".format(
                    newBook['ISBN'].data, newBook['Author3'].data)
                cur.execute(query3)
                db.connection.commit()

            if newBook['Category2'].data:
                query5 = "INSERT INTO Categories(ISBN, Category_name) VALUES ('{}','{}');".format(
                    newBook['ISBN'].data, newBook['Category2'].data)
                cur.execute(query5)
                db.connection.commit()

            if newBook['Category3'].data:
                query6 = "INSERT INTO Categories(ISBN, Category_name) VALUES ('{}','{}');".format(
                    newBook['ISBN'].data, newBook['Category3'].data)
                cur.execute(query6)
                db.connection.commit()

            cur.close()
            flash("Book inserted successfully :)", "success")
            return redirect(url_for('landing'))
        except Exception as e:
            flash(str(e), "danger")

    return render_template("create_Books1.html", pageTitle="Insert Book", form=form)


@app.route("/queriesAdmin1_init")
def getqueriesAdmin1_init():
    try:
        cur = db.connection.cursor()
        # here we have borrows per school of all time
        cur.execute(
            "SELECT S.School_id School, count(borrow_id) 'No_Borrows' FROM borrows B INNER JOIN Book_copies BC ON B.Book_id = BC.Book_id RIGHT JOIN School_Library S ON S.Library_id = BC.Library_id GROUP BY School_id;")
        column_names = [i[0] for i in cur.description]
        Numbers = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()

        return render_template("queriesAdmin1.html", Numbers=Numbers, pageTitle="Sort Borrows by Time")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/queriesAdmin1", methods=["GET", "POST"])
def getqueriesAdmin1():
    try:
        if (request.method == 'POST'):
            if (request.form['type'].lower() != 'any'):
                type2 = request.form['type'].lower()
                month = request.form['month']
                year = request.form['year']
                if type2 == 'year':

                    cur = db.connection.cursor()
                    cur.execute(
                        f"SELECT S.School_id School, count(borrow_id) 'No_Borrows' FROM borrows B INNER JOIN Book_copies BC ON B.Book_id = BC.Book_id RIGHT JOIN School_Library S ON S.Library_id = BC.Library_id WHERE year(borrow_date) = {year} GROUP BY School_id;")
                    column_names = [i[0] for i in cur.description]

                elif type2 == 'month':

                    cur = db.connection.cursor()
                    cur.execute(
                        f"SELECT S.School_id School, count(borrow_id) 'No_Borrows' FROM borrows B INNER JOIN Book_copies BC ON B.Book_id = BC.Book_id RIGHT JOIN School_Library S ON S.Library_id = BC.Library_id WHERE month(borrow_date) = {month} GROUP BY School_id ORDER BY School_id, year(borrow_date), month(borrow_date);")
                    column_names = [i[0] for i in cur.description]

                elif type2 == 'year and month':

                    cur = db.connection.cursor()
                    cur.execute(
                        f"SELECT S.School_id School, count(borrow_id) 'No_Borrows' FROM borrows B INNER JOIN Book_copies BC ON B.Book_id = BC.Book_id RIGHT JOIN School_Library S ON S.Library_id = BC.Library_id WHERE month(borrow_date) = {month} AND year(borrow_date) = {year} GROUP BY School_id ORDER BY School_id, year(borrow_date), month(borrow_date);")
                    column_names = [i[0] for i in cur.description]

                Numbers = [dict(zip(column_names, entry))
                           for entry in cur.fetchall()]
                cur.close()
                return render_template("queriesAdmin1.html", Numbers=Numbers, pageTitle="Sort Borrows by Time")
            else:
                cur = db.connection.cursor()
                # default any
                cur.execute(
                    f"SELECT S.School_id School, count(borrow_id) 'No_Borrows' FROM borrows B INNER JOIN Book_copies BC ON B.Book_id = BC.Book_id RIGHT JOIN School_Library S ON S.Library_id = BC.Library_id GROUP BY School_id;")
                column_names = [i[0] for i in cur.description]
                Numbers = [dict(zip(column_names, entry))
                           for entry in cur.fetchall()]
                cur.close()
                return render_template("queriesAdmin1.html", Numbers=Numbers, pageTitle="Sort Borrows by Time")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        return redirect(url_for('index'))
        # flash(str(e), "danger")
        # abort(500)


@app.route("/queriesAdmin2_init")
def getqueriesAdmin2_init():
    try:

        cur = db.connection.cursor()
        cur.execute(
            f"SELECT A.Author_name FROM Books B INNER JOIN (SELECT ISBN,Category_name FROM Categories WHERE Category_name = 'Young Adult') as C ON B.isbn = C.isbn INNER JOIN Authors A ON A.ISBN = B.ISBN GROUP BY Author_name")
        column_names = [i[0] for i in cur.description]
        q1 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        cur = db.connection.cursor()
        cur.execute(
            f"SELECT U.User_id, U.Full_name FROM Book_copies BC INNER JOIN (SELECT ISBN,Category_name FROM Categories WHERE Category_name = 'Young Adult') as C ON BC.isbn = C.isbn INNER JOIN Borrows B ON B.Book_id = BC.Book_id INNER JOIN Users U ON U.User_id = B.User_id")
        column_names = [i[0] for i in cur.description]
        q2 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        return render_template("queriesAdmin2.html", q1=q1, q2=q2, pageTitle="Find data by Category")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/queriesAdmin2", methods=["GET", "POST"])
def getqueriesAdmin2():
    try:
        if (request.method == 'POST'):

            data = request.form['data']

            cur = db.connection.cursor()
            cur.execute(
                f"SELECT A.Author_name FROM Books B INNER JOIN (SELECT ISBN,Category_name FROM Categories WHERE Category_name = '{data}') as C ON B.isbn = C.isbn INNER JOIN Authors A ON A.ISBN = B.ISBN GROUP BY Author_name")
            column_names = [i[0] for i in cur.description]
            q1 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()

            cur = db.connection.cursor()
            cur.execute(
                f"SELECT U.User_id, U.Full_name FROM Book_copies BC INNER JOIN (SELECT ISBN,Category_name FROM Categories WHERE Category_name = '{data}') as C ON BC.isbn = C.isbn INNER JOIN Borrows B ON B.Book_id = BC.Book_id INNER JOIN Users U ON U.User_id = B.User_id")
            column_names = [i[0] for i in cur.description]
            q2 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
            cur.close()

            return render_template("queriesAdmin2.html", q1=q1, q2=q2, pageTitle="Find data by Category")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        # return redirect(url_for('index'))
        # flash(str(e), "danger")
        abort(500)


@app.route("/queriesAdmin")
def getqueriesAdmin():
    try:
        cur = db.connection.cursor()
        cur.execute("SELECT U.User_id,U.Full_name, COUNT(borrow_id) No_Borrows FROM borrows B INNER JOIN Users U ON U.User_id = B.User_id INNER JOIN Basic_Users BU ON BU.User_id = U.User_id WHERE (YEAR(CURRENT_DATE)-YEAR(U.Date_of_birth)<40) AND Type = 'Teacher' GROUP BY User_id ORDER BY No_Borrows DESC LIMIT 3;")
        column_names = [i[0] for i in cur.description]
        q1 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        cur = db.connection.cursor()
        cur.execute("SELECT A.Author_name FROM Book_copies BC INNER JOIN Authors A ON A.ISBN = BC.ISBN LEFT JOIN Borrows Bo ON Bo.Book_id = BC.Book_id GROUP BY Author_name HAVING Count(borrow_id) = 0;")
        column_names = [i[0] for i in cur.description]
        q2 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        cur = db.connection.cursor()
        cur.execute("SELECT DISTINCT T.Operator_id Operator_1,T2.Operator_id Operator_2, T.C FROM (SELECT L.Operator_id, COUNT(Bo.borrow_id) AS C FROM Book_copies BC INNER JOIN (SELECT Borrow_id,Book_id FROM Borrows WHERE YEAR(CURRENT_DATE)-YEAR(Borrow_date)) Bo ON Bo.Book_id = BC.Book_id INNER JOIN School_Library L ON L.Library_id = BC.Library_id GROUP BY L.Operator_id HAVING C >= 15) AS T INNER JOIN (SELECT L.Operator_id,COUNT(Bo.borrow_id) AS C FROM Book_copies BC INNER JOIN (SELECT Borrow_id,Book_id FROM Borrows WHERE YEAR(CURRENT_DATE)-YEAR(Borrow_date)) Bo ON Bo.Book_id = BC.Book_id INNER JOIN School_Library L ON L.Library_id = BC.Library_id GROUP BY L.Operator_id HAVING C >= 15) AS T2 ON T.C = T2.C WHERE T.Operator_id != T2.Operator_id ORDER BY C;")
        column_names = [i[0] for i in cur.description]
        q3 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        q3 = q3[::2]
        cur.close()

        cur = db.connection.cursor()
        cur.execute("SELECT Cat1, Cat2, COUNT(Borrow_id) No_borrows FROM (SELECT C1.Category_name Cat1, C2.Category_name Cat2, C1.ISBN FROM Categories C1 INNER JOIN Categories C2 ON C1.ISBN = C2.ISBN WHERE C1.Category_name != C2.Category_name) AS T INNER JOIN Book_copies BC ON BC.ISBN = T.ISBN INNER JOIN Borrows Bo ON Bo.Book_id = BC.Book_id GROUP BY Cat1, Cat2 ORDER BY No_borrows DESC LIMIT 3;")
        column_names = [i[0] for i in cur.description]
        q4 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        cur = db.connection.cursor()
        cur.execute("SELECT Author_name, Count(ISBN) C FROM Authors GROUP BY Author_name HAVING C <= (SELECT Count(ISBN) C FROM Authors A GROUP BY Author_name ORDER BY C DESC LIMIT 1) - 5;")
        column_names = [i[0] for i in cur.description]
        q5 = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        cur = db.connection.cursor()
        cur.execute(
            "SELECT Author_name, Count(ISBN) C FROM Authors A GROUP BY Author_name ORDER BY C DESC LIMIT 1;")
        column_names = [i[0] for i in cur.description]
        q5b = [dict(zip(column_names, entry)) for entry in cur.fetchall()]
        cur.close()

        return render_template("queriesAdmin.html", pageTitle="Administrator info - [queries (3-7)]", q1=q1, q2=q2, q3=q3, q4=q4, q5=q5, q5b=q5b)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)


@app.route("/queriesOp1", methods=["GET", "POST"])
def getqueriesOp1():
    if (request.method == 'POST'):
        if (request.form['type'].lower() != 'any'):
            type2 = request.form['type'].lower()
            data = request.form['data']
            if type2 == 'title':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) AS 'Authors', GROUP_CONCAT(DISTINCT Category_name) AS 'Categories', (SELECT CAST(AVG(Score) AS DECIMAL(3,2)) FROM Reviews WHERE ISBN = BC.ISBN) AS Score, B.Total_copies, GROUP_CONCAT(DISTINCT Book_id) AS 'IDs', BC.Library_id AS Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN WHERE B.Title = '{data}' GROUP BY ISBN, Lib;")
                column_names = [i[0] for i in cur.description]

            elif type2 == 'author':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Category_name) AS 'Categories', CASE WHEN Au2 IS NULL THEN Au1 ELSE CONCAT(Au1, ', ', Au2) END AS 'Authors', (SELECT CAST(AVG(Score) AS DECIMAL(3,2)) FROM Reviews WHERE ISBN = BC.ISBN) AS Score, B.Total_copies, GROUP_CONCAT(DISTINCT Book_id) AS 'IDs', BC.Library_id AS 'Library' FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN (SELECT ISBN, Author_name AS Au1 FROM Authors WHERE Author_name = '{data}') C1 ON C1.ISBN = BC.ISBN LEFT JOIN (SELECT ISBN, Author_name AS Au2 FROM Authors WHERE Author_name != '{data}') C2 ON C2.ISBN = BC.ISBN INNER JOIN Categories A ON A.ISBN = BC.ISBN GROUP BY ISBN, Library;")
                column_names = [i[0] for i in cur.description]

            elif type2 == 'category':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) AS 'Authors', CASE WHEN Cat2 IS NULL THEN Cat1 ELSE CONCAT(Cat1, ', ', Cat2) END AS 'Categories', (SELECT CAST(AVG(Score) AS DECIMAL(3,2)) FROM Reviews WHERE ISBN = BC.ISBN) AS Score, B.Total_copies, GROUP_CONCAT(DISTINCT Book_id) AS 'IDs', BC.Library_id AS 'Library' FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN (SELECT ISBN, Category_name AS Cat1 FROM Categories WHERE Category_name = '{data}') C1 ON C1.ISBN = BC.ISBN LEFT JOIN (SELECT ISBN, Category_name AS Cat2 FROM Categories WHERE Category_name != '{data}') C2 ON C2.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = BC.ISBN GROUP BY ISBN, Library;")
                column_names = [i[0] for i in cur.description]

            elif type2 == 'total_copies':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) AS 'Authors', GROUP_CONCAT(DISTINCT Category_name) AS 'Categories', (SELECT CAST(AVG(Score) AS DECIMAL(3,2)) FROM Reviews WHERE ISBN = BC.ISBN) AS Score, B.Total_copies, GROUP_CONCAT(DISTINCT Book_id) AS 'IDs', BC.Library_id AS Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN WHERE Total_copies = {data} GROUP BY ISBN, Lib;")
                column_names = [i[0] for i in cur.description]

            Books = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()
            return render_template("queriesOp1.html", Books=Books, pageTitle="Search Books")
        else:
            cur = db.connection.cursor()
            cur.execute("SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) AS 'Authors', GROUP_CONCAT(DISTINCT Category_name) AS 'Categories', (SELECT CAST(AVG(Score) AS DECIMAL(3,2)) FROM Reviews WHERE ISBN = BC.ISBN) AS Score, B.Total_copies, GROUP_CONCAT(DISTINCT Book_id) AS 'IDs', BC.Library_id AS Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN GROUP BY ISBN, Lib;")
            column_names = [i[0] for i in cur.description]
            Books = [dict(zip(column_names, entry))
                     for entry in cur.fetchall()]
            cur.close()
            return render_template("queriesOp1.html", Books=Books, pageTitle="Search Books")
    else:
        return redirect(url_for('index'))


@app.route("/queriesOp1_init", methods=["GET", "POST"])
def getqueriesOp1_init():
    try:

        cur = db.connection.cursor()
        cur.execute("SELECT BC.ISBN, B.Title, B.Publication_date, GROUP_CONCAT(DISTINCT Author_name) AS 'Authors', GROUP_CONCAT(DISTINCT Category_name) AS 'Categories', (SELECT CAST(AVG(Score) AS DECIMAL(3,2)) FROM Reviews WHERE ISBN = BC.ISBN) AS Score, B.Total_copies, GROUP_CONCAT(DISTINCT Book_id) AS 'IDs', BC.Library_id AS Lib FROM Book_copies BC INNER JOIN Books B ON B.ISBN = BC.ISBN INNER JOIN Categories C ON C.ISBN = BC.ISBN INNER JOIN Authors A ON A.ISBN = C.ISBN GROUP BY ISBN, Lib;")
        column_names = [i[0] for i in cur.description]
        Books = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()
        return render_template("queriesOp1.html", Books=Books, pageTitle="Books Operator Check")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)

    return render_template("queriesOp1.html", Books=Books, pageTitle="Books Operator Check")


@app.route("/queriesOp2", methods=["GET", "POST"])
def getqueriesOp2():
    if (request.method == 'POST'):
        if (request.form['type'].lower() != 'any'):
            type2 = request.form['type'].lower()
            data = request.form['data']
            if type2 == 'name':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT B.User_id, U.Full_name, B.Borrow_id, B.Book_id, Datediff(CURRENT_DATE,BORROW_DATE)-7 days_late FROM Borrows B INNER JOIN Users U ON U.User_id = B.User_id WHERE Datediff(CURRENT_DATE,BORROW_DATE)>7 AND U.Full_name = '{data}' AND Return_date  IS  NULL;")
                column_names = [i[0] for i in cur.description]

            elif type2 == 'late':

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT B.User_id, U.Full_name, B.Borrow_id, B.Book_id, Datediff(CURRENT_DATE,BORROW_DATE)-7 days_late FROM Borrows B INNER JOIN Users U ON U.User_id = B.User_id WHERE Datediff(CURRENT_DATE,BORROW_DATE)=(7 + {data}) AND Return_date IS NULL;")
                column_names = [i[0] for i in cur.description]

            q2 = [dict(zip(column_names, entry))
                  for entry in cur.fetchall()]
            cur.close()
            return render_template("queriesOp2.html", q2=q2, pageTitle="Operator Check")
        else:
            cur = db.connection.cursor()
            cur.execute("SELECT B.User_id, U.Full_name, B.Borrow_id, B.Book_id, Datediff(CURRENT_DATE,BORROW_DATE)-7 days_late FROM Borrows B INNER JOIN Users U ON U.User_id = B.User_id WHERE Datediff(CURRENT_DATE,BORROW_DATE)>7 AND Return_date IS NULL ;")
            column_names = [i[0] for i in cur.description]
            q2 = [dict(zip(column_names, entry))
                  for entry in cur.fetchall()]
            cur.close()
            return render_template("queriesOp2.html", q2=q2, pageTitle="Operator Check")
    else:
        return redirect(url_for('index'))


@app.route("/queriesOp2_init", methods=["GET", "POST"])
def getqueriesOp2_init():
    try:

        cur = db.connection.cursor()
        cur.execute("SELECT B.User_id, U.Full_name, B.Borrow_id, B.Book_id, Datediff(CURRENT_DATE,BORROW_DATE)-7 days_late FROM Borrows B INNER JOIN Users U ON U.User_id = B.User_id WHERE Datediff(CURRENT_DATE,BORROW_DATE)>7 AND Return_date IS NULL ;")
        column_names = [i[0] for i in cur.description]
        q2 = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()
        return render_template("queriesOp2.html", q2=q2, pageTitle="Operator Check")
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)

    return render_template("queriesOp2.html", q2=q2, pageTitle="Operator Check")


@app.route("/queriesOp3", methods=["GET", "POST"])
def getqueriesOp3():
    if (request.method == 'POST'):
        if (request.form['type'].lower() != 'any'):
            data1 = request.form['data1']
            data2 = request.form['data2']
            type2 = request.form['type']

            if type2 == 'user':
                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT U.Username,R.User_id,CAST(AVG(Score) AS DECIMAL(3,2)) AS Average_Score,Count(Score) No_reviews FROM Reviews R INNER JOIN Users U ON U.User_id = R.User_id WHERE R.User_id = {data1}")
                column_names = [i[0] for i in cur.description]
                q2 = [dict(zip(column_names, entry))
                      for entry in cur.fetchall()]
                cur.close()
                return render_template("queriesOp3.html", q2=q2, pageTitle="Operator Check", check2=True, check3=False)

            elif type2 == 'category':
                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT Category_name ,CAST(AVG(R.Score) AS DECIMAL(3,2)) AS Average_Score, Count(Score) No_reviews FROM Reviews AS R INNER JOIN Categories C ON C.ISBN = R.ISBN WHERE Category_name = '{data2}'")
                column_names = [i[0] for i in cur.description]
                q3 = [dict(zip(column_names, entry))
                      for entry in cur.fetchall()]
                cur.close()
                return render_template("queriesOp3.html", q3=q3, pageTitle="Operator Check", check2=False, check3=True)

            elif type2 == 'user_and_category':
                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT U.Username,R.User_id,CAST(AVG(Score) AS DECIMAL(3,2)) AS Average_Score,Count(Score) No_reviews FROM Reviews R INNER JOIN Users U ON U.User_id = R.User_id WHERE R.User_id = {data1}")
                column_names = [i[0] for i in cur.description]
                q2 = [dict(zip(column_names, entry))
                      for entry in cur.fetchall()]
                cur.close()

                cur = db.connection.cursor()
                cur.execute(
                    f"SELECT Category_name ,CAST(AVG(R.Score) AS DECIMAL(3,2)) AS Average_Score, Count(Score) No_reviews FROM Reviews AS R INNER JOIN Categories C ON C.ISBN = R.ISBN WHERE Category_name = '{data2}'")
                column_names = [i[0] for i in cur.description]
                q3 = [dict(zip(column_names, entry))
                      for entry in cur.fetchall()]
                cur.close()

                return render_template("queriesOp3.html", q2=q2, q3=q3, pageTitle="Operator Check", check2=True, check3=True)

        else:
            cur = db.connection.cursor()
            cur.execute("SELECT U.Username,R.User_id,CAST(AVG(Score) AS DECIMAL(3,2)) AS Average_Score,Count(Score) No_reviews FROM Reviews R INNER JOIN Users U ON U.User_id = R.User_id GROUP BY User_id")
            column_names = [i[0] for i in cur.description]
            q2 = [dict(zip(column_names, entry))for entry in cur.fetchall()]
            cur.close()

            cur = db.connection.cursor()
            cur.execute("SELECT Category_name ,CAST(AVG(R.Score) AS DECIMAL(3,2)) AS Average_Score, Count(Score) No_reviews FROM Reviews AS R INNER JOIN Categories C ON C.ISBN = R.ISBN Group BY Category_name")
            column_names = [i[0] for i in cur.description]
            q3 = [dict(zip(column_names, entry))for entry in cur.fetchall()]
            cur.close()
            return render_template("queriesOp3.html", q2=q2, q3=q3, pageTitle="Operator Check", check2=True, check3=True)
    else:
        return redirect(url_for('index'))


@app.route("/queriesOp3_init", methods=["GET", "POST"])
def getqueriesOp3_init():
    try:

        cur = db.connection.cursor()
        cur.execute("SELECT U.Username,R.User_id,CAST(AVG(Score) AS DECIMAL(3,2)) AS Average_Score,Count(Score) No_reviews FROM Reviews R INNER JOIN Users U ON U.User_id = R.User_id GROUP BY User_id")
        column_names = [i[0] for i in cur.description]
        q2 = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()

        cur = db.connection.cursor()
        cur.execute("SELECT Category_name ,CAST(AVG(R.Score) AS DECIMAL(3,2)) AS Average_Score, Count(Score) No_reviews FROM Reviews AS R INNER JOIN Categories C ON C.ISBN = R.ISBN Group BY Category_name")
        column_names = [i[0] for i in cur.description]
        q3 = [dict(zip(column_names, entry))for entry in cur.fetchall()]
        cur.close()

        return render_template("queriesOp3.html", q2=q2, q3=q3, pageTitle="Operator Check", check2=True, check3=True)
    except Exception as e:
        # if the connection to the database fails, return HTTP response 500
        flash(str(e), "danger")
        abort(500)
