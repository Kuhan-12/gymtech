from flask import Flask,request,render_template,redirect,url_for
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import bcrypt,generate_password_hash,check_password_hash,Bcrypt
import sqlalchemy
import datetime
from User.Use import dataUrl
from database import db,Registration,Payment
from User.manager import User
from Admin.admin import adminRoute
from Admin.function import data
from flask.sessions import SecureCookieSessionInterface
from flask import g
from flask_mail import Mail, Message
import json
import random
import os

login_manager=LoginManager()
app = Flask(__name__)
bcrypt = Bcrypt(app)
mail = Mail()
mail.init_app(app)

app.config['MAIL_SERVER']='smtp.zoho.in'
app.config['MAIL_PORT'] =  587
app.config['MAIL_USERNAME'] = 'info@foliagelandscaping.com.au'
app.config['MAIL_PASSWORD'] = 'newLimited@123'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False
mail = Mail(app)
mail.connect()

app.config['SQLALCHEMY_DATABASE_URI']='mysql+pymysql://sanjeev:sanjeev-techpath@202.176.1.150/gymtech'
db.init_app(app)
login_manager.init_app(app)
app.secret_key = os.urandom(24)
func = data(app)

app.register_blueprint(dataUrl)
app.register_blueprint(adminRoute)

@app.before_request
def before_request():
    g.user=current_user

@login_manager.user_loader
def load_user(user_id):
    try:
        with app.app_context():
            user = db.session.query(Registration).filter_by(User_Id=user_id).first()
        if user:
            return User(user.User_Id, user.Username, user.Password)
    except:
        return redirect('/loginPage')

@app.route('/loginPage', methods=['GET','POST'])
def login(): 
    try:
        if request.method=="POST":
            Username = request.form.get("Username")
            Password = request.form.get("Password")
            with app.app_context():
                user = db.session.query(Registration).filter_by(Username=Username).first()
                # print(user.Type)
                isUser=bcrypt.check_password_hash(user.Password, Password) 
            if isUser:
                login_user(User(user.User_Id,user.Username,user.Password))
                if user.Type=="Admin":
                        return redirect(url_for('admin.panel',id = user.User_Id))
                else:    
                    return redirect(url_for('home'))
        return render_template('login.html')
    except ConnectionError:
        return redirect('/loginPage')
    except sqlalchemy.exc.OperationalError:
        return redirect('/loginPage')
    except AttributeError:
        return redirect('/loginPage')
    
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect('/')

@login_manager.unauthorized_handler
def unauthorized():
    return redirect('/loginPage')

@app.errorhandler(404)
def page_not_found(self):
    return render_template('error.html')

@app.route('/')
def home():
    if current_user.is_authenticated:
        user=Registration.query.filter_by(Username=current_user.Username).first()
        pric = func.Query_Plan()
        l=len(pric)
        product=[]
        for row in pric:
            dt={"order_id":func.generate_order_id(row.Price), "price":int(row.Price), "plans_id":row.Plans_Id, "customer_id":user.User_Id}
            product.append(dt)
        return render_template('/user/index.html',user=user,product=product,price=pric,l=l)
    else:
        return render_template('/user/index.html')

@app.route("/Trainers")
def trainers():
    trainer = func.trainer_data()
    return render_template('/user/trainers.html',trainer=trainer)

@app.route('/Equipments')
def equipments():
    equipments_data = func.Equipment_Data()
    return render_template('/user/equipments.html',equipments=equipments_data)

@app.route('/loginPage/forgot_password',methods=["POST","GET"])
def forgot_password():
    if request.method=='POST':
        req = request.form
        Username = req.get('Username')
        Email = req.get('Email')
        user = db.session.query(Registration).filter_by(Username=Username).first()
        email = db.session.query(Registration).filter_by(Email=Email).first()
        user.OTP = random.randint(1000,9999)
        otp = []
        otp.append(user.OTP)
        if email:
            msg = Message('Verification', sender = 'info@foliagelandscaping.com.au', recipients = [email.Email])
            msg.body = "Your Verification Code is"+" "+str(user.OTP)
            mail.send(msg)
        db.session.commit()
        return redirect(url_for('verification',userId=user.User_Id))
    if request.method=='GET':
        return render_template('forgotpassword.html')

@app.route('/loginPage/verification/<userId>',methods=['GET','POST'])
def verification(userId):
    try:
        if request.method=="POST":
            req = request.form
            otp = req.get('otp')
            quer = Registration.query.filter_by(OTP=otp).first()
            Password = req.get('Password')
            quer.Password=generate_password_hash(Password)
            db.session.commit()
            return redirect('/loginPage')
        if request.method=='GET':
            query = Registration.query.filter_by(User_Id=userId).first()
            return render_template('verification.html',user=query)
    except AttributeError:
            return redirect(url_for('verification',userId=quer.User_Id))

@app.route("/webhooks-payment",methods=['POST'])
@login_required
def webhooks():
    pay_data = dict(request.form.lists())
    order_id = pay_data['razorpay_order_id'][0]
    payment_id = pay_data['razorpay_payment_id'][0]
    status=int(pay_data['status_code'][0])
    if status==200:
        statusValue="Success"
    else:
        statusValue="failed"
    order = Payment.query.filter_by(Order_Id_RZP=order_id).first()
    order.Payment_Id_RZP = payment_id
    order.Status = statusValue
    db.session.commit()
    return 'Success'

@app.route('/order_update',methods=['POST'])
@login_required
def order_update():
    order_data = json.loads(request.data.decode('utf-8'))
    status = "Initiated"
    date = datetime.date.today()
    order = Payment(
        Order_Id_RZP = order_data['Order_id'],
        Customer_Id = order_data['User'],
        Plan_Id = order_data['Plan'],
        Status = status,
        Date = date
    )
    db.session.add(order)
    db.session.commit()
    return "success"


if __name__=="__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)