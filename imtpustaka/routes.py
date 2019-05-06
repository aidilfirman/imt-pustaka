import os
import secrets
import pytz
from PIL import Image
from datetime import datetime
from datetime import timedelta
from flask import render_template, url_for, flash, redirect, request
from imtpustaka import app, db, bcrypt
from imtpustaka.forms import RegistrationForm, LoginForm, UpdateAccountForm, RenterForm, BookForm, ReturnForm, SearchForm
from imtpustaka.models import User, Book, Log
from flask_login import login_user, current_user, logout_user, login_required

db.create_all()

@app.route("/", methods=['GET', 'POST'])
def awal():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.id.desc()).paginate(page=page, per_page=10)
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('home.html', books=books, form2=form2)
@app.route("/home", methods=['GET', 'POST'])
def home():
    page = request.args.get('page', 1, type=int)
    books = Book.query.order_by(Book.id.desc()).paginate(page=page, per_page=10)
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('home.html', books=books, form2=form2)

@app.route("/category/<string:category>", methods=['GET', 'POST'])
def category_book(category):
    page = request.args.get('page', 1, type=int)
    books = Book.query.filter_by(category=category).order_by(Book.id.desc()).paginate(page=page, per_page=10, error_out=False)
    books2 = Book.query.filter_by(category=category).first()
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('category_book.html', books=books, books2=books2, form2=form2)

@app.route("/terpopuler", methods=['GET', 'POST'])
def popular():
    page = request.args.get('page', 1, type=int)
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    books = Book.query.order_by(Book.count.desc()).paginate(page=page, per_page=10, error_out=False)
    return render_template('popular.html', books=books, form2=form2)

@app.route("/about", methods=['GET', 'POST'])
def about():
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('about.html', title='About', form2=form2)


@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, nim=form.nim.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Akun berhasil terdaftar, Silahkan masuk', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash('Berhasil masuk', 'success')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Tidak berhasil masuk. Tolong cek email dan password anda!', 'danger')
    return render_template('login.html', title='Login', form=form)


@app.route("/logout")
def logout():
    logout_user()
    flash('Berhasil keluar', 'success')
    return redirect(url_for('home'))


@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        current_user.password = hashed_password
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Akun anda berhasil diupdate!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form, form2=form2)

@app.route("/renter/<int:id>", methods=['GET', 'POST'])
@login_required
def renter(id):
    books = Book.query.filter_by(id=id).first()
    logs = Log.query.filter_by(title_id=id).order_by(Log.id.desc()).first()
    if books.availability:
        form = RenterForm()
        if form.validate_on_submit():
            if bcrypt.check_password_hash(current_user.password, form.password.data):
                log = Log(title=books.title, title_id=id, name_id=current_user.id, name=current_user.username)
                books.availability = False
                books.count += 1
                db.session.add(log)
                db.session.commit()
                flash('Buku berhasil dipinjam', 'success')
                return redirect(url_for('my_book', name=current_user.username))
            else:
                flash('Peminjaman belum berhasil. Silahkan cek password anda', 'danger')
    else:
        user = User.query.filter_by(id=logs.name_id).first() 
        flash('Buku sedang dipinjam oleh ' + user.username, 'danger')
        return redirect(url_for('home'))
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('renter.html', title='Peminjaman', form=form, form2=form2, books=books)

@app.route("/buku/tambah", methods=['GET', 'POST'])
@login_required
def tambah_buku():
    if current_user.nim == 18100000:
        form = BookForm()
        if form.validate_on_submit():
            book = Book(title=form.title.data, category=form.category.data)
            db.session.add(book)
            db.session.commit()
            flash('Buku berhasil ditambahkan', 'success')
            return redirect(url_for('home'))
    else:
        flash('Anda tidak memiliki otoritas pada halaman ini', 'danger')
        return redirect(url_for('home'))
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('tambah_buku.html', title='Buku Baru', form=form, form2=form2)

@app.route("/log", methods=['GET', 'POST'])
@login_required
def log():
    if current_user.nim == 18100000:
        page = request.args.get('page', 1, type=int)
        logs = Log.query.order_by(Log.id.desc()).paginate(page=page, per_page=10)
    else:
        flash('Anda tidak memiliki otoritas pada halaman ini', 'danger')
        return redirect(url_for('home'))
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('log.html', logs=logs, form2=form2)

@app.route("/buku/<string:name>", methods=['GET', 'POST'])
@login_required
def my_book(name):
    page = request.args.get('page', 1, type=int)
    name=current_user.username
    logs = Log.query.filter_by(name_id=current_user.id).filter_by(date_end=None).order_by(Log.id.desc()).paginate(page=page, per_page=10, error_out=False)
    logs2 = Log.query.filter_by(name_id=current_user.id).filter_by(date_end=None).first()
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('my_book.html', title='Buku Saya', logs=logs, logs2=logs2, form2=form2)

@app.route("/return/<int:id>", methods=['GET', 'POST'])
@login_required
def return_book(id):
    books = Book.query.filter_by(id=id).first()
    logs = Log.query.filter_by(title_id=id).filter_by(name_id=current_user.id).filter_by(date_end=None).first()
    form = ReturnForm()
    if form.validate_on_submit():
        book = Book.query.filter_by(id=id).first()
        book.availability = True
        logs.date_end=datetime.now()+timedelta(hours=7)
        db.session.commit()
        flash('Buku berhasil dikembalikan', 'success')
        return redirect(url_for('my_book', name=current_user.username))
    form2 = SearchForm(request.form)
    if request.method == 'POST':
        kata ='%' + form2.data['kata'].title() + '%'
        return redirect(url_for('search',kata=kata))
    return render_template('return_book.html', title='Pengembalian', form=form, form2=form2, logs=logs)

@app.route("/search/<string:kata>", methods=['GET', 'POST'])
def search(kata):
    page = request.args.get('page', 1, type=int)
    hasil = Book.query.filter(Book.title.like(kata)).paginate(page=page, per_page=10)
    return render_template('search.html', title='Hasil Pencarian', hasil=hasil, kata=kata)