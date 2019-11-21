from tenderingSystem import db, login_manager
from datetime import datetime
from flask_login import UserMixin


@login_manager.user_loader
def load_user(user_id):
    return Users.query.get(int(user_id))


class Users(db.Model, UserMixin):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(100), nullable=False)
    user_type = db.Column(db.String(8), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
    company = db.relationship("Company", backref="affiliate", lazy=True)

    def __repr__(self):
        return f"Users('{self.email}', '{self.user_type}')"


class Company(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100), nullable=False, unique=True)
    phone_number = db.Column(db.String(15), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    company_type = db.Column(db.String(50), nullable=True)
    user = db.Column(db.INTEGER, db.ForeignKey("users.id"), nullable=False, unique=True)
    tender_publisher = db.relationship("Tenders", backref="publisher", lazy=True)
    bid_publisher = db.relationship("Bid", backref="bid_publisher", lazy=True)

    def __repr__(self):
        return f"Company('{self.company_name}', '{self.address}', '{self.company_type}')"


bidTender = db.Table("bidTender",
                     db.Column("id", db.INTEGER, primary_key=True, autoincrement=True),
                     db.Column("bid_id", db.INTEGER, db.ForeignKey("bid.id")),
                     db.Column("tender_id", db.INTEGER, db.ForeignKey("tenders.id")),
                     db.Column("date_submitted", db.DATETIME, default=datetime.utcnow())
                     )


class Tenders(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    entity_name = db.Column(db.String(50), nullable=False)
    entity_type = db.Column(db.String(30), nullable=False)
    title = db.Column(db.String(200), nullable=False, unique=True)
    status = db.Column(db.String(8), nullable=False)
    date_published = db.Column(db.DATETIME, default=datetime.utcnow(), nullable=False)
    date_closed = db.Column(db.DATETIME, nullable=False)
    tender_document = db.Column(db.String(100), nullable=False)
    company = db.Column(db.INTEGER, db.ForeignKey("company.id"))
    is_delete = db.Column(db.Boolean, default=False)
    bidTender = db.relationship('Bid', secondary=bidTender, lazy='dynamic',
                                backref=db.backref('tenders', lazy=True))

    def __repr__(self):
        return f"Tenders('{self.entity_name}', '{self.title}', '{self.status}', '{self.date_published}'," \
               f" '{self.date_closed}', '{self.tender_document}', '{self.is_delete}')"


class Bid(db.Model):
    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    bid_document = db.Column(db.String(50), nullable=False)
    date_submitted = db.Column(db.DATETIME, default=datetime.utcnow())
    # is_deleted = db.Column(bd.Boolean, default=False)
    bid_poster = db.Column(db.INTEGER, db.ForeignKey('company.id'))

    def __repr__(self):
        return f"Bid('{self.bid_document}', '{self.date_submitted}', '{self.bid_poster}'"
