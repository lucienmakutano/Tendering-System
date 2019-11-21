from flask import render_template, url_for, redirect, request, flash
from flask_login import login_required
from tenderingSystem import app, db
from tenderingSystem.forms import UploadBidForm
from tenderingSystem.helper_functions import save_tender_document, get_company_information
from tenderingSystem.model import Tenders, Bid


@app.route('/supplier/supplier_home', methods=["GET", "POST"])
@login_required
def supplier_home():
    tenders = Tenders.query.filter_by(is_delete=False).all()
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


@app.route('/supplier/my-bids', methods=['GET', 'POST'])
def my_bids():
    company = get_company_information()
    if company:
        bids = db.engine.execute(f"SELECT * FROM bidTender JOIN Bid ON bidTender.bid_id=Bid.id JOIN Tenders "
                                 f"On bidTender.tender_id=Tenders.id WHERE bid_poster={company.id}")
        return render_template('supplier/myBids.html', bids=bids)
    return render_template('supplier/myBids.html')
