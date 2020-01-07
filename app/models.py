from flask_login import UserMixin
from sqlalchemy import CheckConstraint
from flask import session
from . import db, login_manager


# 管理员表
class Admin(db.Model):
    __tablename__ = 'Admin'

    Ano = db.Column(db.SMALLINT, primary_key=True, autoincrement=True)  # 管理员号
    Fno = db.Column(db.CHAR(10), db.ForeignKey("Faculty.Fno"))  # 教职工号

    # 反向应用  https://blog.csdn.net/hellosweet1/article/details/80171371
    faculty = db.relationship("Faculty", backref=db.backref('admins'))

    def __init__(self, Fno):
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
class Faculty(UserMixin, db.Model):
    __tablename__ = 'Faculty'

    Fno = db.Column(db.CHAR(10), primary_key=True)  # 教职工号
    Fname = db.Column(db.CHAR(16), nullable=False)  # 姓名
    Fsex = db.Column(db.Enum('男', '女'))  # 性别
    Fdept = db.Column(db.String(32))  # 系别
    Fdegree = db.Column(db.Enum('本科', '硕士', '博士', '博士后'), default='本科')  # 学历
    Ftitle = db.Column(db.Enum('助教', '讲师', '副教授', '教授'), default='助教')  # 职称
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


# 图书表
class Book(db.Model):
    __tablename__ = 'Book'

    Bno = db.Column(db.CHAR(13), primary_key=True)  # 国际标准书号 ISBN
    Bname = db.Column(db.String(64), nullable=False)  # 书名
    Bauthor = db.Column(db.String(64), nullable=False)  # 作者
    Bbrief = db.Column(db.String(255))  # 简介
    Bpress = db.Column(db.String(64))  # 出版社
    Brank = db.Column(db.BOOLEAN, default=False)  # 图书级别 true 表示教职工级别 false 表示学生级别
    Btype = db.Column(db.SMALLINT, db.ForeignKey('BookType.Btid'))  # 图书类别
    Wno = db.Column(db.CHAR(10), db.ForeignKey('Warehouse.Wno'))  # 书库号
    Bshelf = db.Column(db.CHAR(10), nullable=False)  # 货架号
    Bdate = db.Column(db.CHAR(16))  # 入库时间
    Bnote = db.Column(db.String(64))  # 备注

    warehouse = db.relationship('Warehouse', backref=db.backref('books'))
    booktype = db.relationship('BookType', backref=db.backref('books'))

    def __init__(self, Bno, Bname, Bauthor, Bbrief, Bpress, Brank, Btype, Wno, Bshelf, Bdate, Bnote):
        self.Bno = Bno
        self.Bname = Bname
        self.Bauthor = Bauthor
        self.Bbrief = Bbrief
        self.Bpress = Bpress
        self.Brank = Brank
        self.Btype = Btype
        self.Wno = Wno
        self.Bshelf = Bshelf
        self.Bdate = Bdate
        self.Bnote = Bnote

    def __repr__(self):
        return '<Book %r>' % self.Bno


# 库存表
class Inventory(db.Model):
    __tablename__ = 'Inventory'
    barcode = db.Column(db.String(6), primary_key=True)
    isbn = db.Column(db.ForeignKey('Book.Bno'))
    storage_date = db.Column(db.String(13))
    withdraw = db.Column(db.Boolean, default=False)  # 是否注销
    status = db.Column(db.Boolean, default=True)  # 是否在馆
    admin = db.Column(db.ForeignKey('Admin.Ano'))  # 入库操作员

    def __repr__(self):
        return '<Inventory %r>' % self.barcode


# 借书记录表
class Query(db.Model):
    __tablename__ = 'Query'

    Qno = db.Column(db.SMALLINT, primary_key=True, autoincrement=True)  # 序号
    Qname = db.Column(db.ForeignKey('Student.Sno'), index=True)  # 用户号
    Bno = db.Column(db.CHAR(13), db.ForeignKey('Book.Bno'), nullable=False)  # 书号
    Midentifiter = db.Column(db.ForeignKey('Inventory.barcode'), index=True)  # 标识符 barcode
    Qbdate = db.Column(db.CHAR(16), nullable=False)  # 借出日期
    Qvalidity = db.Column(db.CHAR(16), nullable=False)  # 有效期
    Qrdate = db.Column(db.CHAR(16), nullable=True)  # 归还日期
    borrow_admin = db.Column(db.ForeignKey('Admin.Ano'))  # 借书操作员
    return_admin = db.Column(db.ForeignKey('Admin.Ano'), nullable=True)  # 还书操作员

    book = db.relationship('Book', backref=db.backref('querys'))

    def __init__(self, Qname, Bno, Midentifiter, Qbdate, Qvalidity):
        self.Qname = Qname
        self.Bno = Bno
        self.Midentifiter = Midentifiter
        self.Qbdate = Qbdate
        self.Qvalidity = Qvalidity

    def __repr__(self):
        return '<Query %r>' % self.Qno


# 图书类别表
class BookType(db.Model):
    __tablename__ = 'BookType'

    Btid = db.Column(db.SMALLINT, primary_key=True, autoincrement=True)
    Btype = db.Column(db.String(32), unique=True)
    Balive = db.Column(db.Boolean, default=True)

    def __init__(self, Btype):
        self.Btype = Btype

    def __repr__(self):
        return '<BookType %r>' % self.Btype


# 书库表
class Warehouse(db.Model):
    __tablename__ = 'Warehouse'

    Wno = db.Column(db.CHAR(4), primary_key=True)  # 书库号
    Wspace = db.Column(db.INT, nullable=False)  # 剩余空间 可以存放多少书
    Wtype = db.Column(db.CHAR(32), unique=True)  # 书库类型
    Walive = db.Column(db.Boolean, default=True)  # 是否删除

    def __init__(self, Wno, Wspace, Wtype):
        self.Wno = Wno
        self.Wspace = Wspace
        self.Wtype = Wtype

    def __repr__(self):
        return '<Warehouse %r>' % self.Wno


# 更新记录表
class Record(db.Model):
    __tablename__ = 'Record'

    Rno = db.Column(db.SMALLINT, primary_key=True, autoincrement=True)  # 序号
    Rdate = db.Column(db.CHAR(16))  # 更新日期
    Bno = db.Column(db.CHAR(13), db.ForeignKey('Book.Bno'), nullable=False)  # 国际标准书号
    Ano = db.Column(db.SMALLINT, db.ForeignKey('Admin.Ano'), nullable=False)  # 管理员号
    Rnote = db.Column(db.String(255))  # 备注

    book = db.relationship('Book', backref=db.backref('records'))
    admin = db.relationship('Admin', backref=db.backref('records'))

    def __init__(self, Rdate, Bno, Ano, Rnote):
        self.Rdate = Rdate
        self.Bno = Bno
        self.Ano = Ano
        self.Rnote = Rnote

    def __repr__(self):
        return '<Record %r>' % self.Rno


# 书库管理记录表
class Library(db.Model):
    __tablename__ = 'Library'

    Lno = db.Column(db.SMALLINT, primary_key=True, autoincrement=True)  # 序号
    Ano = db.Column(db.SMALLINT, db.ForeignKey('Admin.Ano'), nullable=False)  # 管理员号
    Wno = db.Column(db.CHAR(10), db.ForeignKey('Warehouse.Wno'), nullable=False)  # 书库号
    Ldate = db.Column(db.CHAR(16))  # 操作时间
    Lnote = db.Column(db.String(255))

    admin = db.relationship('Admin', backref=db.backref('libraries'))
    warehouse = db.relationship('Warehouse', backref=db.backref('libraries'))

    def __init__(self, Ano, Wno, Lnote):
        self.Ano = Ano
        self.Wno = Wno
        self.Lnote = Lnote

    def __repr__(self):
        return '<Library %r>' % self.Lno


# 唯一标记表
class Mark(db.Model):
    __tablename__ = 'Mark'

    Mid = db.Column(db.BIGINT, primary_key=True, autoincrement=True)  # id
    Bno = db.Column(db.CHAR(13), db.ForeignKey('Book.Bno'))  # 书号
    Midentifiter = db.Column(db.CHAR(10), nullable=False)  # 标识符

    book = db.relationship('Book', backref=db.backref('marks'))

    def __init__(self, Bno, Midentifiter):
        self.Bno = Bno
        self.Midentifiter = Midentifiter

    def __repr__(self):
        return '<Mark %r>' % self.Mid


@login_manager.user_loader
def load_user(Uno):
    if session['account_type'] == 'student':
        print(session['account_type'])
        print("load----->", Student.query.get(Uno))
        return Student.query.get(Uno)
    elif session['account_type'] == 'faculty':
        print(session['account_type'])
        print("load----->", Faculty.query.get(Uno))
        return Faculty.query.get(Uno)
    else:
        return None
