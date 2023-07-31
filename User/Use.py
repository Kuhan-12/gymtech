from flask import Blueprint,render_template,flash,request,redirect,url_for
from flask_login import login_user
from database import db,Registration
from User.manager import User
from flask_bcrypt import bcrypt,generate_password_hash

dataUrl = Blueprint('dataUrl',__name__)

@dataUrl.route('/SignUp',methods=['GET','POST'])
def submit():    
    if request.method=="POST":
        sub = request.form
        username = Registration.query.filter_by(Username=sub.get("Username")).all()
        email = Registration.query.filter_by(Email=sub.get("Email")).all()
        contact = Registration.query.filter_by(Contact=sub.get("Contact")).all()
        if username:
            flash('Already There!','error')
            return render_template('/user/join.html')
        elif email:
            flash('Already There!','same')
            return render_template('/user/join.html')
        elif contact:
            flash('Already There!','there')
            return render_template('/user/join.html')
        user = Registration(
            Fullname=sub.get("Fullname"),
            Username = sub.get("Username"),
            Email=sub.get("Email"),
            Contact = sub.get("Contact"),
            Password = sub.get("Password"),
            Gender=sub.get("Gender"),
            Type = sub.get("Type"),
            Paid = 0
            )
        confirm_password=sub.get("Confirm")
        if len(user.Contact)<10 or len(user.Contact)>10:
            flash('Enter Valid Number','Invalid')
            return render_template('/user/join.html')
        elif confirm_password != sub.get("Password"):
            flash('Password and Confirm Password do not Match!','do_not_match')
            return render_template('/user/join.html')
        else:
            user.Password=generate_password_hash(user.Password)
            db.session.add(user)
            db.session.commit()
            print(user.User_Id)
            try:
                login_user(User(user.User_Id,user.Username,user.Password))
                return redirect(url_for('mainApp.User_Page',name=user.Fullname))
            except RecursionError:
                return redirect('/SignUp')
            except db.DataError:
                return redirect('/SignUp')
    if request.method=='GET':
        return render_template('/user/join.html')