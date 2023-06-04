from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, IntegerField, DateField, PasswordField, TextAreaField
from wtforms.validators import DataRequired, Email, NumberRange, Length, Optional


class Users_form(FlaskForm):
    Username = StringField(label="Username", validators=[
                           DataRequired(message="Username is a required field.")])

    Password = PasswordField(label="Password", validators=[
                             Length(min=5, message='Too short')])

    Date_of_birth = DateField(label="Date of birth", validators=[
                              DataRequired(message="Date of birth is a required field.")])

    Full_name = StringField(label="Full name", validators=[
                            DataRequired(message="Full name is a required field.")])

    Email = StringField(label="Email", validators=[DataRequired(
        message="Email is a required field."), Email(message="Invalid email format.")])

    Type = SelectField(label="Type", choices=[("Administrator", "Administrator"), ("Operator", "Operator"), ("Teacher", "Teacher"), ("Student", "Student")], validators=[DataRequired(
        message="Type is a required field.")])

    School_id = StringField(label="School ID")

    submit = SubmitField("Create")


class School_form(FlaskForm):
    Address = StringField(label="Address", validators=[
                          DataRequired(message="Address is a required field.")])

    City = StringField(label="City", validators=[
                       DataRequired(message="City is a required field.")])

    Phone_number = StringField(label="Phone number", validators=[DataRequired(
        message="Phone number is a required field.")])

    Email = StringField(label="Email", validators=[DataRequired(
        message="Email is a required field."), Email(message="Invalid email format.")])

    Director_name = StringField(label="Director", validators=[
                                DataRequired(message="Director is a required field.")])

    submit = SubmitField("Create")


class Library_form(FlaskForm):
    School_id = SelectField(label="School ID", validators=[DataRequired(
        message="School ID is a required field.")], coerce=int)

    Operator_id = SelectField(label="Operator ID", validators=[DataRequired(
        message="Operator ID is a required field.")], coerce=int)

    submit = SubmitField("Create")


class Books_form(FlaskForm):
    ISBN = StringField(label="ISBN", validators=[
                       DataRequired(message="ISBN is a required field.")])

    Library_id = StringField(label="Library ID", validators=[DataRequired(
        message="Library ID is a required field.")])

    Title = StringField(label="Book Title", validators=[
                        DataRequired(message="Book Title is a required field.")])

    Publisher = StringField(label="Publisher", validators=[
                            DataRequired(message="Publisher is a required field.")])

    Publication_date = DateField(label="Publication Date", validators=[
                                 DataRequired(message="Publication Date is a required field.")])

    Page_count = StringField(label="Number of pages")

    Summary = TextAreaField(label="Summary", validators=[
                            DataRequired(message="Summary is a required field.")])

    Image = StringField(label="Image link", validators=[
        DataRequired(message="Image is a required field.")])

    Language = StringField(label="Language")

    Keywords = StringField(label="Keywords")

    Total_copies = StringField(label="Total Copies", validators=[DataRequired(
        message="Total Copies is a required field.")])

    Author1 = StringField(label="Author 1", validators=[
                          DataRequired(message="Total Copies is a required field.")])

    Author2 = StringField(label="Author 2")

    Author3 = StringField(label="Author 3")

    Category1 = StringField(label="Category 1", validators=[
                            DataRequired(message="Total Copies is a required field.")])

    Category2 = StringField(label="Category 2")

    Category3 = StringField(label="Category 3")

    submit = SubmitField("Create")


# class Book_copies_form(FlaskForm):

#    submit = SubmitField("Create")


class Borrows_form(FlaskForm):
    Borrow_date = DateField(label="Borrow Date (default today)")

    Return_date = DateField(label="Return Date (optional)")

    User_id = StringField(label="User that Borrowed", validators=[
                          DataRequired(message="This is a required field.")])

    Book_id = StringField(label="Book that was Borrowed", validators=[
                          DataRequired(message="This is a required field.")])

    submit = SubmitField("Create")


class Reservations_form(FlaskForm):
    User_id = StringField(label="User that Reserves", validators=[
                          DataRequired(message="This is a required field.")])
    
    Reservation_date = DateField(label="Reservation Date (default today)")

    Pickup_date = DateField(label="Pickup Date (optional)", validators=[Optional()])

    Book_id = StringField(label="Book for Reservation", validators=[
                          DataRequired(message="This is a required field.")])

    Status = SelectField('Status', choices=[
                         ('GRANTED', 'GRANTED'), ('PENDING', 'PENDING'), ('DENIED', 'DENIED')])

    submit = SubmitField("Create")


class Reviews_form(FlaskForm):
    ISBN = StringField(label="Book under Review", validators=[
                       DataRequired(message="This is a required field.")])

    User_id = StringField(label="User that Reviewed", validators=[
                          DataRequired(message="This is a required field.")])

    Score = SelectField('Score', choices=[(str(i), str(i)) for i in range(
        1, 6)], validators=[DataRequired(message="Score is a required field.")])


    Text = TextAreaField(label="Review Comment")

    Status = SelectField('Score', choices=[('GRANTED', 'GRANTED'), ('PENDING', 'PENDING'), ('DENIED', 'DENIED')], validators=[
                         DataRequired(message="Score is a required field.")])

    submit = SubmitField("Create")


class Categories_form(FlaskForm):
    Category_name = StringField(label="Category", validators=[
                                DataRequired(message="Category is a required field.")])

    ISBN = StringField(label="ISBN", validators=[
                       DataRequired(message="ISBN is a required field.")])

    submit = SubmitField("Create")


class Authors_form(FlaskForm):
    Author_name = StringField(label="Author", validators=[
                              DataRequired(message="Author is a required field.")])

    ISBN = SelectField(label="ISBN", validators=[
                       DataRequired(message="ISBN is a required field.")])

    submit = SubmitField("Create")
