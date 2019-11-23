from flask import render_template, url_for, redirect, request, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
from tenderingSystem import app, bcrypt, db
from tenderingSystem.model import Tenders
from tenderingSystem.forms import RegisterForm, LoginForm, NewsLetter, UpdateCompanyForm, CompanyForm, UserForm
from tenderingSystem.helper_functions import get_company_information, return_path
from tenderingSystem.model import Users, Company


#########################################################################################################
@app.route('/', methods=["GET", "POST"])
def welcome():
    form = NewsLetter()
    if form.validate_on_submit():
        pass
    return render_template('landingpage/welcome.html', form=form)


@app.route('/login', methods=["POST", "GET"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = Users.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)

            if user.user_type == "supplier":
                return redirect(url_for('supplier_home'))
            elif user.user_type == "buyer":
                return redirect(url_for('buyer_home'))
        else:
            flash("email or password is incorrect. please try again")
    return render_template('login/login.html', form=form)


@app.route('/register', methods=["POST", "GET"])
def register():
    form = RegisterForm()
    if request.method == "GET":
        return render_template('register/register.html', form=form)
    else:
        if form.validate_on_submit():
            email = form.email.data
            user_type = form.user_type.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')

            user = Users(email=email, password=hashed_password, user_type=user_type)
            db.session.add(user)
            db.session.commit()

            login_user(user)

            if form.user_type.data == "supplier":
                return redirect(url_for('supplier_home'))
            elif form.user_type.data == "buyer":
                return redirect(url_for('buyer_home'))
    return render_template('register/register.html', form=form)


@app.route('/subscribe', methods=["POST"])
def subscribe():
    pass
    return redirect(url_for('welcome'))


@app.route('/account/company_information', methods=["GET", "POST"])
@login_required
def company_information():
    form = CompanyForm()
    update_form = UpdateCompanyForm()
    company = get_company_information()
    if request.method == "GET":
        if company:
            update_form.company_name.data = company.company_name
            update_form.company_type.data = company.company_type
            update_form.phone_number.data = company.phone_number
            update_form.address.data = company.address
            return render_template('company_info.html', company=company, update_form=update_form)
        else:
            return render_template('company_info.html', form=form)
    else:
        if form.validate_on_submit():
            company_name = form.company_name.data
            company_type = form.company_type.data
            phone = form.phone_number.data
            address = form.address.data

            company = Company(company_name=company_name, company_type=company_type,
                              phone_number=phone, address=address, user=current_user.id)
            db.session.add(company)
            db.session.commit()
            flash(f"welcome {company_name}. we are glad to have you here. ")
            return redirect(url_for('company_information'))
    return render_template('buyer/company_info.html', form=form, company_name=company.company_name)


##########################################################################################################
@app.route('/account/update/company-information', methods=["POST", "GET"])
@login_required
def update_company_information():
    form = UpdateCompanyForm()
    company = get_company_information()
    if request.method == "GET":
        return render_template("errors/404.html")
    else:
        if form.validate_on_submit():
            company.company_name = form.company_name.data
            company.company_type = form.company_type.data
            company.phone_number = form.phone_number.data
            company.address = form.address.data
            db.session.commit()
            flash("your information was updated successfully", "success")
            return redirect(url_for('company_information'))
    return render_template('company_info.html', company=company, update_form=form)

###########################################################################################################
@app.route('/account/user_information', methods=["GET", "POST"])
@login_required
def user_information():
    form = UserForm()
    # company = get_company_information()
    # , company_name=company.company_name
    if request.method == "GET":
        form.email.data = current_user.email
        form.password.data = current_user.password
    else:
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            db.session.commit()
            flash("you have successfully updated your account credentials")
            return redirect(url_for('user_information'))
    return render_template('user_info.html', form=form)


##############################################################################################################
@app.route("/download-bid-document/<string:document_name>")
@login_required
def download_bds_document(document_name):
    return send_file(return_path('bid', document_name))


##############################################################################################################
@app.route("/download-tender-document/<string:document_name>")
@login_required
def download_tender_document(document_name):
    return send_file(return_path('tender', document_name))

##############################################################################################################
@app.route('/all-tenders')
def all_tenders():
    page = request.args.get("page", 1, type=int)
    tender = Tenders.query.paginate(page=page, per_page=2)
    return render_template("others/tenders.html", tenders=tender)
##############################################################################################################
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))
