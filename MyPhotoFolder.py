from datetime import datetime
from flask import render_template
from sqlalchemy import distinct, extract
from sqlalchemy import func

from models import app, db, MyFile


def get_years():
    years = db.session.query(distinct(extract('year', MyFile.created_date)))\
        .order_by(MyFile.created_date)
    return [row[0] for row in years]

def get_months(year):
    # Select distinct months in the year
    months = db.session.query(distinct(extract('month', MyFile.created_date)))\
        .filter(extract('year', MyFile.created_date) == year)\
        .order_by(MyFile.created_date)
    return [row[0] for row in months]

@app.template_filter('month_name')
def _jinja_month_name(month):
    return datetime.strptime(str(month), '%m').strftime('%B')

@app.route('/')
def index():
    # Select 300 random files
    my_files = MyFile.query.order_by(func.random()).limit(300)

    return render_template('index.html', my_files=my_files, years=get_years())

@app.route('/date/<int:year>/')
def year(year):

    # Select 100 random files from the year
    my_files_year = MyFile.query.filter(extract('year', MyFile.created_date) == year)\
        .order_by(func.random())\
        .limit(100)

    return render_template('date.html',
                           my_files=my_files_year.all(),
                           current_year=year,
                           years=get_years(),
                           months=get_months(year))


@app.route('/date/<int:year>/<int:month>/')
def month(year, month):

    # Select all files filtered by month
    my_files_month = MyFile.query\
        .filter(extract('year', MyFile.created_date) == year, extract('month', MyFile.created_date) == month)\
        .order_by(MyFile.created_date)

    return render_template('date.html',
                           my_files=my_files_month.all(),
                           current_year=year,
                           current_month=month,
                           years=get_years(),
                           months=get_months(year))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5002)
