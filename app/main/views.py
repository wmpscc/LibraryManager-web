from . import main
from .forms import Login, Logon
from flask import flash, redirect, url_for, session, render_template, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
import time
from datetime import datetime, date
from .. import db
from ..models import Admin, Student, Faculty


# ******************************* 注册登录相关 *******************************
@main.route('/', methods=['GET', 'POST'])
def login():
    form = Login()
    if form.validate_on_submit():
        if form.choose.data == 'student':
            user = Student.query.filter_by(Sno=form.account.data, Spassword=form.password.data).first()
            if user is not None:
                login_user(user)
                session['account_type'] = form.choose.data
                session['uid'] = form.account.data
                print("login---->", user)
        elif form.choose.data == 'faculty':
            user = Faculty.query.filter_by(Fno=form.account.data, Fpassword=form.password.data).first()
            if user is not None:
                login_user(user)
                session['account_type'] = form.choose.data
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
                user = Faculty(form.account.data, form.name.data, sex, form.dept.data, '', '', True, form.tel.data,
                               form.email.data, form.password1.data, today_stamp, valid_date)
                db.session.add(user)
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


# ******************************* 图书管理 *******************************

@main.route('/new_store', methods=['GET', 'POST'])
@login_required
def new_store():
    pass
