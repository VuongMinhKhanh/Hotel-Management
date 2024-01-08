import math
from flask import render_template, request, redirect, jsonify
from flask import session as login_session
import os
import dao
from dao import *
from __init__ import app, login, db
from models import *
from flask_login import login_user, current_user, UserMixin, AnonymousUserMixin
import datetime

suite = ""
quantity = ""
checkin_day = ""
checkout_day = ""
is_available = True


def add_images_root(image):
    new_image = ""
    root = "static/img"
    # new_image = os.path.join(root, image)
    new_image = root + "/" + image

    return new_image


@app.route("/")
def home():
    # blogs = get_all_blogs()
    # num = count_blogs()
    # page_size = app.config["PAGE_SIZE"]
    kw = request.args.get("kw")
    # images = dao.get_all_loai_phong()
    suites = {
        "Junior":
            {
                "name": "Junior Suite",
                "wifi": False,
                "bedroom": 1,
                "description": "des 1",
                "image": "room-1.jpg"
            },
        "Executive":
            {
                "name": "Executive Suite",
                "wifi": True,
                "bedroom": 2,
                "description": "des 2",
                "image": "room-2.jpg"

            },
        "Deluxe":
            {
                "name": "Deluxe Suite",
                "wifi": True,
                "bedroom": 3,
                "description": "des 3",
                "image": "room-3.jpg"
            }
    }

    for k, v in suites.items():
        v["image"] = add_images_root(v["image"])
        # print(v["image"])

    return render_template("index.html", suites=suites
                           # , pages=math.ceil(num/page_size)
                           , current_user=current_user)


@login.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route("/admin/login", methods=["post"])
def login_admin():
    username = request.form.get("username")
    password = request.form.get("password")

    user = auth_user(username=username, password=password)

    if user:
        login_user(user)
        if username != "admin":
            return redirect("/")
        else:
            return redirect("/admin")


@app.route('/login', methods=['get', 'post'])
def login_view():
    if request.method.__eq__('POST'):
        username = request.form.get('username')
        password = request.form.get('password')

        user = dao.auth_user(username=username, password=password)
        if user:
            login_user(user)

        next = request.args.get('next')
        if next:
            return redirect(next)

        return redirect("/")

    return render_template('login.html')


@app.route("/api/checkAvail", methods=["post"])
def check_avail():
    data = request.form.to_dict()
    # print(data)
    suite = data.get('suite')
    quantity = data.get('quantity')
    checkin_day = data.get('checkin_day')
    checkout_day = data.get('checkout_day')
    is_available = True


    # if quantity > count_rooms(suite, checkin_day, checkout_day):
    #     is_available = False

    return jsonify(suite)


@app.route('/booking', methods=["get", 'post'])
def booking():
    # if request.method.__eq__('POST'):
    #     return redirect("/booking")

    return render_template('booking.html')


if __name__ == "__main__":
    # import admin
    # app.run(debug=True)
    with app.app_context():
        cki = datetime.datetime(year=datetime.datetime.today().year, month=1, day=8)
        cko = datetime.datetime(year=datetime.datetime.today().year, month=1, day=10)
        print(count_rooms_by_rent_time("Standard - Giường đôi", cki, cko))
