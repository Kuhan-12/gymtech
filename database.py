from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text,Column,Integer,ForeignKey
db = SQLAlchemy()

class Registration(db.Model):
    __tablename__='User'
    User_Id = db.Column(db.Integer,primary_key=True)
    Fullname=db.Column(db.String(100))
    Username = db.Column(db.String(100),unique=True)
    Email=db.Column(db.String(100))
    Contact = db.Column(db.String(10))
    Password = db.Column(db.String(36))
    Gender=db.Column(db.String(10))
    file = db.Column(db.String(255))
    Type = db.Column(db.String(30))
    OTP = db.Column(db.String(255))
    Paid = db.Column(db.String(255))

class Member(db.Model):
    __tablename__='Members'
    Member_Id = db.Column(db.Integer,primary_key=True)
    Trainer_Id = Column(Integer,ForeignKey('Staff.Staff_id'))
    Start_Date = db.Column(db.Date)
    Plan_Id = Column(Integer,ForeignKey('Plans.Plans_Id'))
    Cust_Id = Column(Integer,ForeignKey("User.User_Id"))
    Equipment_Id = Column(Integer,ForeignKey("Equipment.Equipment_Id"))
    Total_Fees = db.Column(db.String(255))

class Staff(db.Model):
    __tablename__='Staff'
    Staff_id = db.Column(db.Integer,primary_key=True)
    Occupation = db.Column(db.String(100))
    Working_Days = db.Column(db.Integer)
    Experience = db.Column(db.String(100))
    Salary = db.Column(db.String(100))
    Fees = db.Column(db.String(100))
    Total = db.Column(db.String(100))
    Reg_Id = Column(Integer,ForeignKey('User.User_Id'))

class Equipment(db.Model):
    __tablename__='Equipment'
    Equipment_Id = db.Column(db.Integer,primary_key=True)
    Name = db.Column(db.String(100))
    Quantity = db.Column(db.String(10))
    Image = db.Column(db.String(255))
    Weight = db.Column(db.String(30))
    Category = db.Column(db.String(255))
    Company = db.Column(db.String(255))
    Equipment_Charge = db.Column(db.String(255))

class Plans(db.Model):
    __tablename__='Plans'
    Plans_Id = db.Column(db.Integer,primary_key=True)
    Plan_Name = db.Column(db.String(100))
    Description = db.Column(db.String(255))
    Price = db.Column(db.String(255))
    Time_Period = db.Column(db.String(255))

class Payment(db.Model):
    __tablename__='Payment'
    Order_Id = db.Column(db.Integer,primary_key=True)
    Customer_Id = Column(Integer,ForeignKey('User.User_Id'))
    Plan_Id = Column(Integer,ForeignKey('Plans.Plans_Id'))
    Date = db.Column(db.Date)
    Order_Id_RZP = db.Column(db.String(255))
    Payment_Id_RZP = db.Column(db.String(255))
    Status = db.Column(db.String(255))