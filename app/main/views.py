from . import main
from .forms import Login, Logon,BorrowForm,SearchStudentForm
from flask import flash, redirect, url_for, session, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import time
from datetime import date
from .. import db
from ..models import Admin, Student, Faculty, BookType, Warehouse, Book, Library,Record,Query,Inventory
import json
from sqlalchemy import or_, and_


# ******************************* 注册登录相关 *******************************
@main.route('/', methods=['GET', 'POST'])
def login():
    form = Login()

    # session['account_type'] = None
    if form.validate_on_submit():
        if form.choose.data == 'student':
            print("student被执行")
            user = Student.query.filter_by(Sno=form.account.data, Spassword=form.password.data).first()
            if user is not None:
                login_user(user)
                session['name'] = user.Sname
                session['account_type'] = form.choose.data
                session['uid'] = form.account.data
                print("login---->", user)
        elif form.choose.data == 'faculty':
            user = Faculty.query.filter_by(Fno=form.account.data, Fpassword=form.password.data).first()
            if user is not None:
                admin = Admin.query.filter_by(Fno=form.account.data).first()
                print('---->', admin)
                if admin is not None:  # 管理员
                    session['admin'] = True
                    session['admin_Ano'] = admin.Ano
                else:
                    session['admin'] = False
                    session['admin_Ano'] = None
                login_user(user)
                session['name'] = user.Fname
                session['account_type'] = form.choose.data
                print(session['account_type'])
                session['uid'] = form.account.data
                print("login---->", user)
        else:
            user = None
        if user is None:
            flash(u"用户名或密码错误，请重新输入")
            return redirect(url_for('.login'))
        else:
            current_user.uid = form.account.data
            print('uid-->', current_user.uid)
            return redirect(url_for('.index'))  # 登录成功

    return render_template('main/login.html', form=form)


@main.route("/logon", methods=['GET', 'POST'])
def logon():
    form = Logon()
    if form.validate_on_submit():
        if form.password1.data != form.password2.data:
            flash(u'请确认密码是否一致！')
        else:
            if form.sex.data == 'man':
                sex = '男'
            else:
                sex = '女'
            today_date = date.today()
            today_str = today_date.strftime("%Y-%m-%d")
            today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
            valid_date = str((int(today_stamp) + 365 * 4 * 86400) * 1000)
            if form.type.data == 'student':
                user = Student(form.account.data, form.name.data, sex, form.dept.data, form.tel.data, form.email.data,
                               today_stamp, valid_date, form.password1.data)
                db.session.add(user)
                db.session.commit()

            elif form.type.data == 'faculty':
                user = Faculty(form.account.data, form.name.data, sex, form.dept.data, '本科', '助教', True, form.tel.data,
                               form.email.data, form.password1.data, today_stamp, valid_date)
                db.session.add(user)
                db.session.commit()

                # 超级管理员
                if user.Fno == 'admin00001':
                    admin = Admin(user.Fno)
                    db.session.add(admin)
                    db.session.commit()

            else:
                flash(u'请完整填写内容！')
                return redirect(url_for('.logon'))
            flash(u'注册成功，请登录!')
            return redirect(url_for('.login'))
    return render_template('main/logon.html', form=form)


@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash(u'您已退出登录！')
    return redirect(url_for('.login'))


# ******************************* 主页、个人信息 *******************************
@main.route('/index', methods=['GET', 'POST'])
@login_required
def index():
    return render_template('main/index.html')

@main.route('/user_info')
@login_required
def user_info():
    print('id----->', session['uid'])
    if session['account_type'] == 'student':
        user = Student.query.filter_by(Sno=session['uid']).first()
        return render_template('main/user-info-stu.html', user=user, name=session.get('Sname'))
    elif session['account_type'] == 'faculty':
        user = Faculty.query.filter_by(Fno=session['uid']).first()
        return render_template('main/user-info-faculty.html', user=user, name=session.get('Fname'))
    else:
        return render_template('main/index.html')


# ******************************* 学生信息查询 ****************************
@main.route('/search_student', methods=['GET', 'POST'])
@login_required
def search_student():
    form = SearchStudentForm()
    if session['group'] == 'student':
        flash(u'您无权限操作！')
    return render_template('main/search-student.html', name=session.get('name'), form=form)


@main.route('/student', methods=['POST'])
def find_student():
    stu = Student.query.filter_by(Sno=request.form.get('card')).first()
    if stu is None:
        return jsonify([])
    else:

        today_date = date.today()
        today_str = today_date.strftime("%Y-%m-%d")
        today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
        today_stamp = str((int(today_stamp)) * 1000)
        return jsonify([{'name': stu.Sname, 'gender': stu.Ssex, 'valid_date': stu.valid_date,
                         'debt': False if stu.valid_date > today_stamp else True}])


@main.route('/record', methods=['POST'])
def find_record():
    records = db.session.query(Query).join(Inventory).join(Book).filter(Query.Qname == request.form.get('card')) \
        .with_entities(Query.Midentifiter, Inventory.isbn, Book.Bname, Book.Bauthor, Query.Qbdate,
                       Query.Qrdate, Query.Qvalidity).all()
    data = []
    for record in records:
        start_date = timeStamp(record.Qbdate)
        due_date = timeStamp(record.Qvalidity)
        end_date = timeStamp(record.Qrdate)
        if end_date is None:
            end_date = '未归还'
        item = {'barcode': record.Midentifiter, 'book_name': record.Bname, 'author': record.Bauthor,
                'start_date': start_date, 'due_date': due_date, 'end_date': end_date}
        data.append(item)
    return jsonify(data)


# ******************************* 工具 ****************************
def timeStamp(timeNum):
    if timeNum is None:
        return timeNum
    else:
        timeStamp = float(float(timeNum) / 1000)
        timeArray = time.localtime(timeStamp)
        print(time.strftime("%Y-%m-%d", timeArray))
        return time.strftime("%Y-%m-%d", timeArray)

# ******************************* 图书管理 *******************************

@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    print(request.form)
    if request.form:
        data = request.form
        Bno = data["Bno"]
        Bname = data["Bname"]
        Bauthor = data["Bauthor"]
        Bbrief = data["Bbrief"]
        Bpress = data["Bpress"]
        Brank = int(data["Brank"])
        Btype = data["Btype"]
        Wno = data["Wno"]
        Bshelf = data["Bshelf"]
        Bnumber = data["Bnumber"]
        Bdate = data["Bdate"]
        Bnote = data["Bnote"]
        book = Book(Bno=Bno, Bname=Bname, Bauthor=Bauthor, Bbrief=Bbrief,
                    Bpress=Bpress, Brank=Brank, Btype=Btype, Wno=Wno, Bshelf=Bshelf, Bdate=Bdate, Bnote=Bnote,
                    Bnumber=Bnumber)
        record=Record(Bno,1,"新建图书")
        db.session.add(book)
        db.session.add(record)
        db.session.commit()
    return render_template('main/new-store.html', res=1)


# 图书展示
@main.route('/show_store', methods=['GET', 'POST'])
@login_required
def show_store():
    return render_template('main/show-book.html')


# 图书查找
@main.route('/select_store', methods=['GET', 'POST'])
@login_required
def select_store():
    form = {
        "code": 0
        , "msg": ""
        , "count": ""
        , "data": []
    }
    page_limit = {}
    for i in request.args.to_dict().keys():
        page_limit = json.loads(i)
    if page_limit['page'] and page_limit['page']:
        page = page_limit['page']
        limit = page_limit['limit']
        data = page_limit['data']
    else:
        page = 1
        limit = 20
        data = ''
    if data == "all" or data == "":
        books = Book.query.filter_by(Balive=True)
        form["count"] = Book.query.filter_by(Balive=True).count()
        books = books.paginate(page=int(page), per_page=int(limit),
                               error_out=True)
    else:
        booktype = BookType.query.filter(BookType.Balive == True, BookType.Btype == data).first()
        if booktype:
            books = Book.query.filter(Book.Balive == True,
                                      or_(Book.Bno.like("%" + data + "%"),
                                          Book.Bname.like("%" + data + "%"),
                                          Book.Bauthor.like("%" + data + "%"),
                                          Book.Bbrief.like("%" + data + "%"),
                                          Book.Bpress.like("%" + data + "%"),
                                          Book.Wno.like("%" + data + "%"),
                                          Book.Bshelf.like("%" + data + "%"),
                                          Book.Bdate.like("%" + data + "%"),
                                          Book.Btype.like("%" + str(booktype.Btid) + "%"),
                                          Book.Bnote.like("%" + data + "%")))
        else:
            books = Book.query.filter(Book.Balive == True,
                                      or_(Book.Bno.like("%" + data + "%"),
                                          Book.Bname.like("%" + data + "%"),
                                          Book.Bauthor.like("%" + data + "%"),
                                          Book.Bbrief.like("%" + data + "%"),
                                          Book.Bpress.like("%" + data + "%"),
                                          Book.Wno.like("%" + data + "%"),
                                          Book.Bshelf.like("%" + data + "%"),
                                          Book.Bdate.like("%" + data + "%"),
                                          Book.Bnote.like("%" + data + "%")))
        form["count"] = books.count()
        books = books.paginate(page=int(page), per_page=int(limit), error_out=True)

    for book in list(books.items):
        form["data"].append({
            "Bno": book.Bno,
            "Bname": book.Bname,
            "Bauthor": book.Bauthor,
            "Bbrief": book.Bbrief,
            "Bpress": book.Bpress,
            "Brank": book.Brank,
            "Btype": book.booktype.Btype,
            "Wno": book.Wno,
            "Bshelf": book.Bshelf,
            "Bdate": book.Bdate,
            "Bnote": book.Bnote
        })
    return jsonify(form)


# 图书删除
@main.route('/delete_store', methods=['GET', 'POST'])
@login_required
def delete_store():
    print(request.form)
    if request.form:
        Book.query.filter(Book.Bno == request.form["Bno"]).update({"Balive": False})
        record=Record(request.form["Bno"],1,"删除图书")
        db.session.add(record)
        db.session.commit()
        return jsonify(1)
    return jsonify(0)


# 图书更新
@main.route('/update_store', methods=['GET', 'POST'])
@login_required
def update_store():
    if request.form:
        data = request.form.to_dict()
        Bno = data["Bno"]
        Bname = data["Bname"]
        Bauthor = data["Bauthor"]
        Bbrief = data["Bbrief"]
        Bpress = data["Bpress"]
        Brank = data["Brank"]
        data["Brank"] = 1 if data["Brank"] == 'true' else 0
        Btype = data["Btype"]
        print(Btype)
        data["Btype"] = BookType.query.filter_by(Btype=Btype).first().Btid
        Wno = data["Wno"]
        Bshelf = data["Bshelf"]
        # Bnumber = data["Bnumber"]
        Bdate = data["Bdate"]
        Bnote = data["Bnote"]
        print(data)
        ware = Book.query.filter(Book.Bno == Bno).update(data)
        record=Record(Bno,1,"更新图书")
        db.session.add(record)
        db.session.commit()
    return jsonify(1)


# 书籍记录
@main.route('/book_note', methods=['GET'])
def book_note():
    return render_template('main/book-note.html')


# 查找图书记录
@main.route('/select_book_note', methods=['POST', 'GET'])
def select_book_note():
    print("**********************************")
    print(request.args.to_dict())
    print(request.form)
    page_limit = {}
    for i in request.args.to_dict().keys():
        page_limit = json.loads(i)
    if page_limit['page'] and page_limit['page']:
        page = page_limit['page']
        limit = page_limit['limit']
        data = page_limit['data']
    else:
        page = 1
        limit = 10
        data = ''
    form = {
        "code": 0
        , "msg": ""
        , "count": ""
        , "data": []
    }
    if data == "all" or data == '':
        records =Record.query.filter()
        form["count"] = Record.query.filter().count()
        records = records.paginate(page=int(page), per_page=int(limit),
                                       error_out=True)
    else:
        records =Record.query.filter(or_(Library.Lnote.like("%" + data + "%"),
                                             Library.Lno.like("%" + data + "%"),
                                             Library.Wno.like("%" + data + "%"),
                                             Library.Ano.like("%" + data + "%"),
                                             Library.Ldate.like("%" + data + "%")))
        form["count"] = records.count()
        records = records.paginate(page=int(page), per_page=int(limit), error_out=True)
    for record in list(records.items):
        form["data"].append({
            "Rno":  record.Rno,
            "Ano":  record.Ano,
            "Bno":  record.Bno,
            "Rdate":  record.Rdate,
            "Rnote":  record.Rnote
        })
    return jsonify(form)


# ******************************* 书库管理 *******************************
# 新建书库
@main.route('/new_ware', methods=['GET', 'POST'])
@login_required
def new_ware():
    print(request.form)
    if request.form:
        message = 0
        Wno = request.form['Wno']
        Wspace = request.form['Wspace']
        Wtype = request.form['Wtype']
        print(Warehouse.query.filter_by(Wno=Wno).first())
        if Warehouse.query.filter_by(Wno=Wno).first():
            return jsonify(message)
        ware = Warehouse(Wno, Wspace, Wtype)
        library = Library(1, Wno, "新建书库")
        db.session.add(ware)
        db.session.add(library)
        db.session.commit()
        message = 1
        return jsonify(message)
    return render_template('main/new-ware.html')


# 显示书库
@main.route('/show_ware', methods=['GET', 'POST'])
@login_required
def show_ware():
    return render_template('main/show-ware.html')


# 查询书库
@main.route('/select_all_ware', methods=['GET', 'POST'])
@login_required
def select_all_ware():
    wares = Warehouse.query.filter_by(Walive=True)
    data = []
    for ware in wares:
        data.append({
            "Wno": ware.Wno,
            "Wtype": ware.Wtype
        })
    return jsonify({"data": data})


# 查询书库
@main.route('/select_ware', methods=['GET', 'POST'])
@login_required
def select_ware():
    print('$$$$$$$$$$$$$$$$')
    print(request.args.to_dict())
    page_limit = {}
    for i in request.args.to_dict().keys():
        page_limit = json.loads(i)
    if page_limit['page'] and page_limit['page']:
        page = page_limit['page']
        limit = page_limit['limit']
        data = page_limit['data']
    else:
        page = 1
        limit = 10
        data = ''
    print('$$$$$$$$$$$$$$$$')
    form = {
        "code": 0
        , "msg": ""
        , "count": ""
        , "data": []
    }
    if data == "all" or data == '':
        wares = Warehouse.query.filter_by(Walive=True)
        form["count"] = Warehouse.query.filter_by(Walive=True).count()
        wares = wares.paginate(page=int(page), per_page=int(limit),
                               error_out=True)
    else:
        wares = Warehouse.query.filter(Warehouse.Walive == True,
                                       or_(Warehouse.Wno.like("%" + data + "%"),
                                           Warehouse.Wspace.like("%" + data + "%"),
                                           Warehouse.Wtype.like("%" + data + "%")))
        form["count"] = wares.count()
        wares = wares.paginate(page=int(page), per_page=int(limit), error_out=True)
    for wa in list(wares.items):
        form["data"].append({
            "Wno": wa.Wno,
            "Wtype": wa.Wtype,
            "Wspace": wa.Wspace,
        })
    return jsonify(form)


# 更新书库
@main.route('/update_ware', methods=['GET', 'POST'])
@login_required
def update_ware():
    data = request.form
    if data:
        Wno = data['Wno']
        Wtype = data['Wtype']
        Wspace = data['Wspace']
        message = 0
        ware = Warehouse.query.filter(Warehouse.Wno == Wno).update({"Wtype": Wtype, "Wspace": Wspace})
        library = Library(1, Wno, "更新书库")
        db.session.add(library)
        db.session.commit()
        message = 1
        return jsonify(message)
    return render_template('main/new-ware.html')


# 删除书库
@main.route('/delete_ware', methods=['GET', 'POST'])
@login_required
def delete_ware():
    data = request.form
    Wno = data['Wno']
    Wtype = data['Wtype']
    message = 0
    ware = Warehouse.query.filter(and_(Warehouse.Wno == Wno, Warehouse.Wtype == Wtype)).update({"Walive": False})
    print(ware)
    if ware:
        library = Library(1, Wno, "删除书库")
        db.session.add(library)
        db.session.commit()
        message = 1
    return jsonify(message)


# 书库日志
@main.route('/ware_note', methods=['GET'])
@login_required
def ware_note():
    return render_template('main/ware-note.html')


# 书库搜索
@main.route('/select_ware_note', methods=['GET', 'POST'])
@login_required
def select_ware_note():
    print("**********************************")
    print(request.args.to_dict())
    print(request.form)
    page_limit = {}
    for i in request.args.to_dict().keys():
        page_limit = json.loads(i)
    if page_limit['page'] and page_limit['page']:
        page = page_limit['page']
        limit = page_limit['limit']
        data = page_limit['data']
    else:
        page = 1
        limit = 10
        data = ''
    form = {
        "code": 0
        , "msg": ""
        , "count": ""
        , "data": []
    }
    if data == "all" or data == '':
        libraries = Library.query.filter()
        form["count"] = Library.query.filter().count()
        libraries = libraries.paginate(page=int(page), per_page=int(limit),
                                       error_out=True)
    else:
        libraries = Library.query.filter(or_(Library.Lnote.like("%" + data + "%"),
                                             Library.Lno.like("%" + data + "%"),
                                             Library.Wno.like("%" + data + "%"),
                                             Library.Ano.like("%" + data + "%"),
                                             Library.Ldate.like("%" + data + "%")))
        form["count"] = libraries.count()
        libraries = libraries.paginate(page=int(page), per_page=int(limit), error_out=True)
    for library in list(libraries.items):
        form["data"].append({
            "Lno": library.Lno,
            "Ano": library.Ano,
            "Wno": library.Wno,
            "Ldate": library.Ldate,
            "Lnote": library.Lnote
        })
    return jsonify(form)


# ******************************* 书类管理 *******************************

# 书类展示
@main.route('/book_type', methods=['GET'])
@login_required
def book_type():
    return render_template("main/book-type.html")


@main.route('/query_all_type', methods=['GET', 'POST'])
@login_required
def query_all_type():
    types = BookType.query.filter_by(Balive=True)
    data = []
    for ty in types:
        data.append({
            "Btid": ty.Btid,
            "Btype": ty.Btype
        })
    return jsonify({"data": data})


@main.route('/query_type', methods=['GET'])
@login_required
def query_type():
    types = BookType.query.filter_by(Balive=True)
    form = {
        "code": 0
        , "msg": ""
        , "count": ""
        , "data": []
    }
    count = 0
    for ty in types:
        count += 1
        form["data"].append({
            "id": count,
            "Btid": ty.Btid,
            "Btype": ty.Btype
        })
    form["count"] = count
    print(form)
    return jsonify(form)


# 新建书类
@main.route('/new_type', methods=['GET', 'POST'])
@login_required
def new_type():
    if request.form:
        Btype = request.form['Btype']
        booktype = BookType.query.filter(BookType.Btype == Btype).first()

        if booktype:
            return jsonify(0)
        else:
            booktype = BookType(Btype)
            db.session.add(booktype)
            db.session.commit()
            return jsonify(1)
    return render_template('main/new-type.html')


# 删除书类
@main.route('/delete_type', methods=['POST', 'GET'])
@login_required
def delete_type():
    message = 0

    if request.form:
        Btype = request.form['Btype']
        type_one = BookType.query.filter(BookType.Btype == Btype).first()

        if type_one:
            type_one.Balive = False
            db.session.commit()
            message = 1
    return jsonify(message)


# 更改书类
@main.route('/update_type', methods=['GET', 'POST'])
@login_required
def update_type():
    print(request.form)
    if request.form:
        booktype = BookType.query.filter(BookType.Btid == request.form["Btid"]).update({"Btype": request.form["Btype"]})
        if booktype:
            return jsonify(1)
    return jsonify(0)

# ******************************* 借书 *******************************

@main.route('/borrow', methods=['GET', 'POST'])
@login_required
def borrow():
    form = BorrowForm()
    # if session['group'] == 'student':
    #     flash(u'您无权限操作！')
    return render_template('main/borrow.html', name=session.get('name'), form=form)


@main.route('/out', methods=['GET', 'POST'])
@login_required
def out():
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    barcode = request.args.get('barcode')
    card = request.args.get('card')
    book_name = request.args.get('book_name')
    isbn = request.args.get('isbn')

    Qbdate = str(int(today_stamp) * 1000)
    Qvalidity = str((int(today_stamp) + 30 * 86400) * 1000)
    print('isbn-->', isbn)
    query = Query(card, isbn, barcode, Qbdate, Qvalidity)
    query.borrow_admin = session['admin_Ano']
    db.session.add(query)
    db.session.commit()

    book = Inventory.query.filter_by(barcode=barcode).first()
    book.status = False
    db.session.add(book)
    db.session.commit()
    bks = db.session.query(Book).join(Inventory).filter(Book.Bname.contains(book_name), Inventory.status == 1). \
        with_entities(Inventory.barcode, Book.Bno, Book.Bname, Book.Bauthor, Book.Bpress).all()
    data = []
    for bk in bks:
        item = {'barcode': bk.barcode, 'isbn': bk.Bno, 'book_name': bk.Bname,
                'author': bk.Bauthor, 'press': bk.Bpress}
        data.append(item)
    return jsonify(data)


@main.route('/find_stu_book', methods=['GET', 'POST'])
def find_stu_book():
    stu = Student.query.filter_by(Sno=request.form.get('card')).first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    if stu is None:
        return jsonify([{'stu': 0}])  # 没找到
    if int(stu.valid_date) < int(today_stamp) * 1000:
        return jsonify([{'stu': 2}])  # 到期

    books = db.session.query(Book).join(Inventory).filter(Book.Bname.contains(request.form.get('book_name')),
                                                          Inventory.status == 1).with_entities(Inventory.barcode,
                                                                                               Book.Bno,
                                                                                               Book.Bname,
                                                                                               Book.Bauthor,
                                                                                               Book.Bpress). \
        all()
    data = []
    for book in books:
        item = {'barcode': book.barcode, 'isbn': book.Bno, 'book_name': book.Bname,
                'author': book.Bauthor, 'press': book.Bpress}
        data.append(item)
    return jsonify(data)


# ******************************* 还书 *******************************

@main.route('/return_book', methods=['GET', 'POST'])
@login_required
def return_book():
    # if session['group'] == 'student':
    #     flash(u'您无权限操作！')
    form = SearchStudentForm()
    return render_template('main/return.html', name=session.get('name'), form=form)


@main.route('/in', methods=['GET', 'POST'])
@login_required
def bookin():
    barcode = request.args.get('barcode')
    card = request.args.get('card')
    query = Query.query.filter(Query.Midentifiter == barcode, Query.Qname == card, Query.Qrdate.is_(None)).first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    query.Qrdate = str(int(today_stamp) * 1000)  # 还书日期
    query.return_admin = session['admin_Ano']
    db.session.add(query)
    db.session.commit()
    book = Inventory.query.filter_by(barcode=barcode).first()
    book.status = True
    db.session.add(book)
    db.session.commit()
    bks = db.session.query(Query).join(Inventory).join(Book).filter(Query.Qname == card,
                                                                    Query.Qrdate.is_(None)).with_entities(
        Query.Midentifiter, Book.Bno, Book.Bname, Query.Qbdate, Query.Qvalidity).all()
    data = []
    for bk in bks:
        start_date = timeStamp(bk.Qbdate)
        due_date = timeStamp(bk.Qvalidity)
        item = {'barcode': bk.Midentifiter, 'isbn': bk.Bno, 'book_name': bk.Bname,
                'start_date': start_date, 'due_date': due_date}
        data.append(item)
    return jsonify(data)


@main.route('/find_not_return_book', methods=['GET', 'POST'])
def find_not_return_book():
    stu = Student.query.filter_by(Sno=request.form.get('card')).first()
    today_date = date.today()
    today_str = today_date.strftime("%Y-%m-%d")
    today_stamp = time.mktime(time.strptime(today_str + ' 00:00:00', '%Y-%m-%d %H:%M:%S'))
    if stu is None:
        return jsonify([{'stu': 0}])  # 没找到
    if int(stu.valid_date) < int(today_stamp) * 1000:
        return jsonify([{'stu': 2}])  # 到期

    books = db.session.query(Query).join(Inventory).join(Book).filter(Query.Qname == request.form.get('card'),
                                                                      Query.Qrdate.is_(None)).with_entities(
        Query.Midentifiter, Book.Bno, Book.Bname, Query.Qbdate, Query.Qvalidity).all()
    data = []
    print('books len-->', len(books))
    for book in books:
        start_date = timeStamp(book.Qbdate)
        due_date = timeStamp(book.Qvalidity)
        item = {'barcode': book.Midentifiter, 'isbn': book.Bno, 'book_name': book.Bname,
                'start_date': start_date, 'due_date': due_date}
        data.append(item)
    return jsonify(data)
