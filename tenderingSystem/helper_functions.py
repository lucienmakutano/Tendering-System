import os
from tenderingSystem import app
import secrets
from tenderingSystem.model import Company
from flask_login import current_user


def save_tender_document(tender_document, sub_directory):
    random_name = secrets.token_hex(8)
    _, file_extension = os.path.splitext(tender_document.filename)
    file_name = random_name + file_extension
    path = os.path.join(app.root_path, 'uploads/' + sub_directory, file_name)
    tender_document.save(path)

    return file_name


def get_company_id():
    company = Company.query.filter_by(user=current_user.id).first()

    if company:
        return company.id


def get_company_information():
    company = Company.query.filter_by(user=current_user.id).first()

    return company


def return_path(sub_directory, file_name):
    return os.path.join(app.root_path, 'uploads/' + sub_directory, file_name)
