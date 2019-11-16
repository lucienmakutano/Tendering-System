from flask import render_template, url_for, redirect, request, flash, send_file
from flask_login import login_user, logout_user, login_required, current_user
import os
from tenderingSystem import app, bcrypt, db
from tenderingSystem.forms import RegisterForm, LoginForm, NewsLetter, TenderForm, CompanyForm, UserForm, \
    UpdateTenderForm, UploadBidForm
from tenderingSystem.helper_functions import save_tender_document, get_company_id, get_company_information, return_path
from tenderingSystem.model import Users, Tenders, Company, Bid


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
def company_information():
    form = CompanyForm()
    company = get_company_information()
    if request.method == "GET":
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


@app.route('/account/user_information', methods=["GET", "POST"])
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


@app.route("/download-tender-document/<string:document_name>")
def download_tender_document(document_name):
    return send_file(return_path('tender', document_name))


##############################################################################################################
@app.route('/supplier/supplier_home', methods=["GET", "POST"])
@login_required
def supplier_home():
    tenders = Tenders.query.all()
    company = get_company_information()
    if company:
        return render_template('supplier/home.html', tenders=tenders, company_name=company.company_name)
    return render_template('supplier/home.html', tenders=tenders)


@app.route('/tender_document/<int:tender_id>', methods=["GET", "POST"])
@login_required
def tender_document(tender_id):
    form = UploadBidForm()
    company = get_company_information()
    tender = Tenders.query.get(tender_id)
    if request.method == "GET":
        if company:
            return render_template('supplier/tender_document.html', form=form, tender=tender,
                                   company_name=company.company_name)
        else:
            render_template('supplier/tender_document.html', form=form, tender=tender)
    else:
        if form.validate_on_submit():
            if company:
                bid_document = save_tender_document(form.bid_document.data, "bid")
                bid = Bid(bid_document=bid_document, bid_poster=company.id)
                db.session.add(bid)
                db.session.commit()
                bid.tenders.append(tender)
                db.session.commit()
                return redirect(url_for('supplier_home'))
            else:
                flash("you have to register as company before you place any bid. ", "warning")
                return render_template('supplier/tender_document.html', form=form, tender=tender)
    return render_template('supplier/tender_document.html', form=form, tender=tender)


################################################################################################################
@app.route('/buyer/buyer_home', methods=["GET", "POST"])
@login_required
def buyer_home():
    company = get_company_information()
    if company:
        if request.method == "GET":
            return render_template('buyer/home.html', company_name=company.company_name)
    else:
        return render_template('buyer/home.html')


@app.route('/buyer/publish_tender', methods=["GET", "POST"])
@login_required
def publish_tender():
    form = TenderForm()
    firm = get_company_information()
    if request.method == "GET":
        if firm:
            return render_template('buyer/tenders.html', form=form, company_name=firm.company_name)
        else:
            return render_template('buyer/tenders.html', form=form)
    else:
        if form.validate_on_submit():
            entity_name = form.entity_name.data
            entity_type = form.entity_type.data
            title = form.title.data
            status = form.status.data
            date_published = form.date_published.data
            date_closed = form.date_closed.data
            tender_documents = form.tender_document.data
            company = get_company_id()

            if company:
                if tender_documents:
                    document_name = save_tender_document(tender_documents, "tender")

                    tender = Tenders(entity_name=entity_name, entity_type=entity_type, title=title,
                                     status=status, date_published=date_published, date_closed=date_closed,
                                     tender_document=document_name, company=company)
                    db.session.add(tender)
                    db.session.commit()
                    flash(f"Your tender has been successfully posted. ", "success")
                    return redirect(url_for('publish_tender'))
                else:
                    flash("you can not put a closing date that is previous the opening date", "danger")
                    return render_template('buyer/tenders.html', form=form, company_name=firm.company_name)
            else:
                flash("you can not post a tender without registering your company. ", "warning")
                return render_template('buyer/tenders.html', form=form)
    return render_template('buyer/tenders.html', form=form)


@app.route('/buyer/view_bids', methods=["GET", "POST"])
@login_required
def view_bids():
    company = get_company_information()
    if company:
        return render_template('buyer/bids.html', company_name=company.company_name)
    return render_template('buyer/bids.html')


@app.route('/buyer/edit_tender', methods=["GET", "POST"])
@login_required
def edit_tender():
    firm = get_company_information()
    form = TenderForm()
    company = get_company_id()
    tenders = Tenders.query.filter_by(company=company).order_by(Tenders.date_published, Tenders.date_closed).all()
    if company:
        return render_template('buyer/edit_tender.html', tenders=tenders, form=form, company_name=firm.company_name)
    return render_template('buyer/edit_tender.html', tenders=tenders, form=form)


@app.route('/buyer/edit_tender/<int:tender_id>', methods=["GET", "POST"])
@login_required
def load_tender(tender_id):
    form = UpdateTenderForm()
    firm = get_company_information()
    company = get_company_id()
    tenders = Tenders.query.filter_by(company=company).order_by(Tenders.date_published, Tenders.date_closed).all()
    editable_tenders = Tenders.query.filter_by(id=tender_id).first()
    tender = Tenders.query.get(tender_id)
    if request.method == "GET":
        return render_template('buyer/edit_tender.html', editable_tenders=editable_tenders, form=form,
                               company_name=firm.company_name, tenders=tenders)

    else:
        if form.validate_on_submit():
            tender.entity_name = form.entity_name.data
            tender.entity_type = form.entity_type.data
            tender.title = form.title.data
            tender.status = form.status.data
            tender.date_published = form.date_published.data
            tender.date_closed = form.date_closed.data
            tender.tender_document = save_tender_document(form.tender_document.data, "tender")
            db.session.commit()
            return redirect(url_for('edit_tender'))
    return render_template('buyer/edit_tender.html', editable_tenders=editable_tenders, form=form,
                           company_name=firm.company_name, tenders=tenders)


@app.route('/buyer/delete_tender/<int:tender_id>', methods=["GET", "POST"])
@login_required
def delete_tender(tender_id):
    firm = get_company_information()
    tender = Tenders.query.get(tender_id)
    if tender:
        if request.method == "GET":
            # tender.deleted = 1
            db.session.commit()
            return redirect(url_for('edit_tender'))
    form = TenderForm()
    company = get_company_id()
    tenders = Tenders.query.filter_by(company=company).order_by(Tenders.date_published, Tenders.date_closed).all()
    return render_template('buyer/edit_tender.html', tenders=tenders, form=form, company_name=firm.company_name)


@app.route('/buyer/report', methods=["GET", "POST"])
@login_required
def get_report():
    company = get_company_information()
    if company:
        return render_template('buyer/report.html', company_name=company.company_name)
    else:
        return render_template('buyer/report.html')


###############################################################################################################
@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('welcome'))
