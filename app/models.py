from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from flask import session
from . import db, login_manager


# 管理员表
class Admin(UserMixin, db.Model):
    __tablename__ = 'Admin'

    Ano = db.Column(db.SMALLINT, primary_key=True, autoincrement=True)  # 管理员号
    Fno = db.Column(db.CHAR(10), db.ForeignKey("Faculty.Fno"))  # 教职工号

    # 反向应用  https://blog.csdn.net/hellosweet1/article/details/80171371
    faculty = db.relationship("Faculty", backref=db.backref('admins'))

    def __init__(self, Ano, Fno):
        self.Ano = Ano
        self.Fno = Fno

    def __repr__(self):
        return '<Admin %r>' % self.Ano


# 学生表
class Student(UserMixin, db.Model):
    __tablename__ = 'Student'

    Sno = db.Column(db.CHAR(10), primary_key=True)  # 学号
    Sname = db.Column(db.String(16), nullable=False)  # 姓名
    Ssex = db.Column(db.Enum('男', '女'))  # 性别
    Sdept = db.Column(db.String(30))  # 院系
    Stel = db.Column(db.CHAR(11), nullable=False)  # 联系电话
    Semail = db.Column(db.String(32))  # 邮箱
    enroll_date = db.Column(db.CHAR(32), nullable=False)  # 注册日期
    valid_date = db.Column(db.CHAR(32), nullable=False)  # 有效日期
    Spassword = db.Column(db.String(32), nullable=False)  # 密码

    def __init__(self, Sno, Sname, Ssex, Sdept, Stel, Semail, enroll_date, valid_date, Spassword):
        self.Sno = Sno
        self.Sname = Sname
        self.Ssex = Ssex
        self.Sdept = Sdept
        self.Stel = Stel
        self.Semail = Semail
        self.enroll_date = enroll_date
        self.valid_date = valid_date
        self.Spassword = Spassword

    def __repr__(self):
        return '<Student %r>' % self.Sno

    def get_id(self):
        return self.Sno

    def verify_password(self, password):
        if password == self.Spassword:
            return True
        else:
            return False


# 教职工表
class Faculty(db.Model):
    __tablename__ = 'Faculty'

    Fno = db.Column(db.CHAR(10), primary_key=True)  # 教职工号
    Fname = db.Column(db.CHAR(16), nullable=False)  # 姓名
    Fsex = db.Column(db.Enum('男', '女'))  # 性别
    Fdept = db.Column(db.String(32))  # 系别
    Fdegree = db.Column(db.Enum('本科', '硕士', '博士', '博士后'))  # 学历
    Ftitle = db.Column(db.Enum('助教', '讲师', '副教授', '教授'))  # 职称
    Fis_work = db.Column(db.BOOLEAN)  # 是否在职   true表示在职，false表示不在职
    Ftel = db.Column(db.CHAR(11))  # 联系电话
    Femail = db.Column(db.String(64))  # 邮箱
    Fpassword = db.Column(db.String(32))  # 密码
    enroll_date = db.Column(db.CHAR(32), nullable=False)  # 注册日期
    valid_date = db.Column(db.CHAR(32), nullable=False)  # 有效日期

    def __init__(self, Fno, Fname, Fsex, Fdept, Fdegree, Ftitle, Fis_work, Ftel, Femail, Fpassword, enroll_date,
                 valid_date):
        self.Fno = Fno
        self.Fname = Fname
        self.Fsex = Fsex
        self.Fdept = Fdept
        self.Fdegree = Fdegree
        self.Ftitle = Ftitle
        self.Ftel = Ftel
        self.Fis_work = Fis_work
        self.Femail = Femail
        self.Fpassword = Fpassword
        self.enroll_date = enroll_date
        self.valid_date = valid_date

    def __repr__(self):
        return '<Faculty %r>' % self.Fno

    def get_id(self):
        return self.Fno

    def verify_password(self, password):
        if password == self.Fpassword:
            return True
        else:
            return False


@login_manager.user_loader
def load_user(Uno):
    if session['account_type'] == 'student':
        print(session['account_type'])
        print("load----->", Student.query.get(Uno))
        return Student.query.get(Uno)
    elif session['account_type'] == 'faculty':
        return Faculty.query.get(Uno)
