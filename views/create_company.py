from flask import Blueprint, render_template, request, session, redirect, url_for, jsonify, flash, send_file
from forms.create_company import CompanyForm
create_company_bp = Blueprint("create_company", __name__)


@create_company_bp.route("/create_company", methods=["GET", "POST"])
def create_company():
    form = CompanyForm()
    return render_template("create_company.html", form=form)
