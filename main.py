import os

from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, current_user, login_required, logout_user
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

basedir = os.path.abspath(os.path.dirname(__file__))

db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = 'sign_in'
login_manager.login_message_category = 'info'

app = Flask(__name__)
app.config['SECRET_KEY'] = "?``§=)()%``ÄLÖkhKLWDO=?)(_:;LKADHJATZQERZRuzeru3rkjsdfLJFÖSJ"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'data.sqlite?check_same_thread=False')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

login_manager.init_app(app)
db.init_app(app)

admin = Admin(app, name='microblog', template_mode='bootstrap3')

association_table = db.Table('association', db.metadata,
                             db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
                             db.Column('group_id', db.Integer, db.ForeignKey('group.id'))
                             )


class User(db.Model, UserMixin):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, unique=True, nullable=False)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)


class Bill(db.Model):
    __tablename__ = 'bill'
    id = db.Column(db.Integer, primary_key=True)
    amount = db.Column(db.String, nullable=False)
    description = db.Column(db.String, nullable=False)
    group_id = db.Column(db.Integer, db.ForeignKey('group.id'))
    group = db.relationship('Group', back_populates='bills')

    def __init__(self, amount, description, group_id):
        self.amount = amount
        self.description = description
        self.group_id = group_id


class Group(db.Model):
    __tablename__ = 'group'
    id = db.Column(db.Integer, primary_key=True)
    group_id = db.Column(db.String, unique=True, nullable=False)
    description = db.Column(db.String, nullable=False)
    bills = db.relationship('Bill', back_populates='group')

    def __init__(self, group_id, description):
        self.group_id = group_id
        self.description = description


class ManoModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated


admin.add_view(ManoModelView(User, db.session))
admin.add_view(ManoModelView(Group, db.session))
admin.add_view(ManoModelView(Bill, db.session))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)


with app.app_context():
    import forms

    db.create_all()


@app.route('/')
def index():
    return render_template('homepage.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    form = forms.SignUpForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password1.data, email=form.email.data)
        db.session.add(user)
        db.session.commit()
        flash(f'Welcome, {user.username}!', 'success')
        return redirect(url_for('index'))
    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = forms.SignInForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if not user:
            flash(f'User {form.email.data} does not exist!', 'danger')
            return redirect(url_for('login'))
        if not form.password.data == user.password:
            flash(f'User / password do not math!', 'danger')
            return redirect(url_for('login'))
        login_user(user)
        flash(f'Welcome, {user.email}', 'success')
        return redirect(url_for('index'))
    return render_template('login.html', form=form)


@app.route('/bills/<group_id>', methods=['GET', 'POST'])
@login_required
def bills(group_id):
    # all_bills = Bill.query.all()
    all_bills = Bill.query.filter_by(group_id=group_id)
    form = forms.BillsForm()
    if form.validate_on_submit():
        new_bill = Bill(amount=form.amount.data, description=form.description.data, group_id=group_id)
        db.session.add(new_bill)
        db.session.commit()
        return redirect(url_for('bills', group_id=group_id))
    return render_template('bills.html', form=form, all_bills=all_bills)


@app.route('/groups', methods=['GET', 'POST'])
@login_required
def groups():
    all_groups = Group.query.all()
    form = forms.GroupsForm()
    if form.validate_on_submit():
        new_group = Group(group_id=form.group_id.data, description=form.description.data)
        if not new_group:
            flash(f'Group ID {form.group_id.data} already exists!', 'danger')
            return redirect(url_for('groups'))
        flash(f' New group ID: {form.group_id.data}', 'success')
        for bill in form.bills.data:
            added_bill = Bill.query.get(bill.id)
            new_group.bills.append(added_bill)
        db.session.add(new_group)
        db.session.commit()
        return redirect(url_for('bills', group_id=new_group.id))
    return render_template('groups.html', form=form, all_groups=all_groups)


@app.route('/sign_out')
@login_required
def sign_out():
    flash(f'See you next time, {current_user.username}')
    logout_user()
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run()
