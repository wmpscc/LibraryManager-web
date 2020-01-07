from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField, PasswordField, RadioField
from wtforms.validators import DataRequired, EqualTo, Length


class Login(FlaskForm):
    account = StringField(u'账号', validators=[DataRequired(), Length(6, 10)])
    password = PasswordField(u'密码', validators=[DataRequired(), Length(5, 32)])
    choice = [('student', u"学生"), ('faculty', u"职工")]
    choose = RadioField(u'类别', choices=choice, validators=[DataRequired()], coerce=str)
    submit = SubmitField(u'登录')


class Logon(FlaskForm):
    account = StringField(u'账号', validators=[DataRequired()])
    password1 = PasswordField(u'密码', validators=[DataRequired()])
    password2 = PasswordField(u'密码', validators=[DataRequired()])
    name = StringField(u'名字', validators=[DataRequired()])
    sex = RadioField(u'性别', choices=[('man', u'男'), ('woman', u'女')], validators=[DataRequired()], coerce=str)
    dept = StringField(u'院系', validators=[DataRequired()])
    tel = StringField(u'电话', validators=[DataRequired()])
    email = StringField(u'邮箱', validators=[DataRequired()])
    type = RadioField(u'账号类型', choices=[('student', u'学生'), ('faculty', u'职工')], validators=[DataRequired()],
                      coerce=str)
    submit = SubmitField(u'注册')


class SearchStudentForm(FlaskForm):
    card = StringField(validators=[DataRequired()])
    submit = SubmitField('搜索')


class BorrowForm(FlaskForm):
    card = StringField(validators=[DataRequired()])
    book_name = StringField(validators=[DataRequired()])
    submit = SubmitField(u'搜索')
