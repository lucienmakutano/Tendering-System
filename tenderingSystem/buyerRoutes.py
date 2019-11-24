from flask import render_template, url_for, redirect, request, flash, jsonify
from flask_login import login_required
from tenderingSystem import app, db
from tenderingSystem.forms import TenderForm, UpdateTenderForm
from tenderingSystem.helper_functions import save_tender_document, get_company_id, get_company_information, json_data
from tenderingSystem.model import Tenders, Company, Bid


@app.route('/buyer/buyer_home', methods=["GET", "POST"])
@login_required
def buyer_home():
    closed_tender = request.args.get('closed_tender', 1, type=int)
    open_tender = request.args.get('open_tender', 1, type=int)
    company = get_company_information()
    closed_tenders = Tenders.query.filter_by(company=company.id, is_delete=False, status="closed") \
        .paginate(page=closed_tender, per_page=5)
    open_tenders = Tenders.query.filter_by(company=company.id, is_delete=False, status="open") \
        .paginate(page=open_tender, per_page=6)
    bids = ""
    if company:
        if request.method == "GET":
            return render_template('buyer/home.html', company_name=company.company_name
                                   , closed_tenders=closed_tenders, open_tenders=open_tenders)
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
                if date_published < date_closed:
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
        tenders = db.engine.execute(f"SELECT * FROM bidTender JOIN Bid ON bidTender.bid_id=Bid.id JOIN Tenders "
                                    f"ON bidTender.tender_id=Tenders.id WHERE company={company.id}")
        return render_template('buyer/bids.html', company_name=company.company_name, tenders=tenders)
    return render_template('buyer/bids.html')


@app.route('/buyer/view_bids/bidder/<int:bidder_id>')
@login_required
def bidder_info(bidder_id):
    bidder = Company.query.get(1)
    company = get_company_information()
    if company:
        tenders = db.engine.execute(f"SELECT * FROM bidTender JOIN Bid ON bidTender.bid_id=Bid.id JOIN Tenders "
                                    f"ON bidTender.tender_id=Tenders.id WHERE company={company.id}")
        return render_template('buyer/bids.html', company_name=company.company_name, tenders=tenders, bidder=bidder)

    return render_template('buyer/bids.html')


@app.route('/buyer/edit_tender', methods=["GET", "POST"])
@login_required
def edit_tender():
    firm = get_company_information()
    form = TenderForm()
    company = get_company_id()
    tenders = Tenders.query.filter_by(company=company, is_delete=False, status="open") \
        .order_by(Tenders.date_published, Tenders.date_closed).all()
    if company:
        return render_template('buyer/edit_tender.html', tenders=tenders, form=form, company_name=firm.company_name)
    return render_template('buyer/edit_tender.html', tenders=tenders, form=form)


@app.route('/buyer/edit_tender/<int:tender_id>', methods=["GET", "POST"])
@login_required
def load_tender(tender_id):
    form = UpdateTenderForm()
    firm = get_company_information()
    company = get_company_id()
    tenders = Tenders.query.filter_by(company=company, is_delete=False, status="open") \
        .order_by(Tenders.date_published, Tenders.date_closed).all()
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


@app.route('/buyer/close-tender/<int:tender_id>')
def close_tender(tender_id):
    company = get_company_id()
    form = TenderForm()
    firm = get_company_information()
    tenders = Tenders.query.filter_by(company=company, is_delete=False, status="open") \
        .order_by(Tenders.date_published, Tenders.date_closed).all()
    tender = Tenders.query.get(tender_id)
    if tender:
        if request.method == "GET":
            tender.status = "closed"
            db.session.commit()
            return redirect(url_for('edit_tender'))
    return render_template('buyer/edit_tender.html', tenders=tenders, form=form, company_name=firm.company_name)


@app.route('/buyer/delete_tender/<int:tender_id>', methods=["GET", "POST"])
@login_required
def delete_tender(tender_id):
    firm = get_company_information()
    tender = Tenders.query.get(tender_id)
    form = TenderForm()
    company = get_company_id()
    tenders = Tenders.query.filter_by(company=company, is_delete=False, status="open") \
        .order_by(Tenders.date_published, Tenders.date_closed).all()
    if tender:
        if request.method == "GET":
            tender.is_delete = 1
            db.session.commit()
            return redirect(url_for('edit_tender'))
    return render_template('buyer/edit_tender.html', tenders=tenders, form=form, company_name=firm.company_name)


@app.route('/buyer/report', methods=["GET", "POST"])
@login_required
def get_report():
    tender_dict = dict()
    company = get_company_information()
    if company:
        return render_template('buyer/report.html', company_name=company.company_name, company_id=company.id)
    else:
        return render_template('buyer/report.html')


@app.route('/buyer/<int:user_id>/graph-data', methods=["GET"])
def graph_data(user_id):
    tender_per_month = []
    jan = json_data(Tenders, 1)
    tender_per_month.append(jan)
    feb = json_data(Tenders, 2)
    tender_per_month.append(feb)
    mar = json_data(Tenders, 3)
    tender_per_month.append(mar)
    apr = json_data(Tenders, 4)
    tender_per_month.append(apr)
    may = json_data(Tenders, 5)
    tender_per_month.append(may)
    june = json_data(Tenders, 6)
    tender_per_month.append(june)
    jul = json_data(Tenders, 7)
    tender_per_month.append(jul)
    aug = json_data(Tenders, 8)
    tender_per_month.append(aug)
    sept = json_data(Tenders, 9)
    tender_per_month.append(sept)
    october = json_data(Tenders, 10)
    tender_per_month.append(october)
    nov = json_data(Tenders, 11)
    tender_per_month.append(nov)
    dec = json_data(Tenders, 12)
    tender_per_month.append(dec)

    # tender_per_month.append(tenders)

    return jsonify({"tender_per_month": tender_per_month})


@app.route('/')
def bid_per_tender():
    pass
