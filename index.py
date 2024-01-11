import math
from flask import render_template, request, redirect, jsonify, session
from flask import session as login_session
import os
import dao
from dao import *
from __init__ import app, login, db
from models import *
from flask_login import login_user, current_user, UserMixin, AnonymousUserMixin
import datetime


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


def list_to_datetime(date):
    return datetime.datetime(year=int(date[0]), month=int(date[1]), day=int(date[2]))


@app.route("/api/checkAvail", methods=["post"])
def check_avail():
    data = request.json
    # print(data)
    room_type = data.get('room_type')
    quantity = data.get('quantity')
    start_date = data.get('checkin_day').split("-")
    sd = datetime.datetime(year=int(start_date[0]), month=int(start_date[1]), day=int(start_date[2]))
    end_date = data.get('checkout_day').split("-")
    ed = datetime.datetime(year=int(end_date[0]), month=int(end_date[1]), day=int(end_date[2]))

    avail_rooms = rooms_by_rent_time(room_type, sd, ed)

    available = len(avail_rooms) >= int(quantity)
    if available:
        info = {
            "room_type": room_type,
            "start_date": start_date,
            "end_date": end_date,
            "avail_rooms": avail_rooms,
        }

        booking_info = session.get('booking_info')
        if booking_info is None:
            booking_info = []

        for bkinfo in booking_info:
            if bkinfo.get("info"):
                bkinfo.get("info").update(info)

                session['booking_info'] = booking_info
                return jsonify(available)

        booking_info.append({"info": info})
        session['booking_info'] = booking_info
    return jsonify(available)


@app.route("/api/retrieveCustomer", methods=["post"])
def retrieve_customer():
    customers = request.json.get("customers")
    booker = request.json.get("booker")
    booking_info = session.get('booking_info')

    # print("1", len(booking_info[0]["info"].get("avail_rooms")))

    for bkinfo in booking_info:
        if bkinfo.get("info"):
            if len(bkinfo.get("info").get("avail_rooms")) * 3 < len(customers):
                return jsonify(False)

    all_customers = []
    for customer in customers:
        all_customers.append(customer)

    for bkinfo in booking_info:
        if bkinfo.get("customers"):
            keys_to_remove = ['customers', 'booker']
            booking_info = [item for item in booking_info if all(key not in item for key in keys_to_remove)]

    booking_info.append({"customers": all_customers})
    booking_info.append({"booker": booker})

    print("booking info:", booking_info)

    session['booking_info'] = booking_info
    return jsonify(booking_info)


@app.route('/booking', methods=["get", 'post'])
def booking():
    # if request.method.__eq__('POST'):
    #     return redirect("/booking")
    if session["booking_info"] is not None:
        session["booking_info"] = None

    return render_template('booking.html', room_types=get_room_types(),
                           receptionists=get_receptionist_names())


@app.route('/booking_2', methods=["get", 'post'])
def booking_2():
    # if request.method.__eq__('POST'):
    #     return redirect("/booking")
    return render_template('booking_2.html')


@app.route('/api/confirm', methods=["get", 'post'])
def confirm():
    booking_info = session.get('booking_info')

    info = next((item['info'] for item in booking_info if 'info' in item), {})
    booker = next((item['booker'] for item in booking_info if 'booker' in item), {})
    customers = next((item['customers'] for item in booking_info if 'customers' in item), [])

    # print(info) # {'avail_rooms': ['301'], 'end_date': ['2024', '01', '10'], 'room_type': 'Deluxe', 'start_date': ['2024', '01', '10']}
    # print(info["avail_rooms"]) # ['301']

    for customer in customers:
        if customer.get("type") == "Nội địa":
            type = LoaiKhach.noi_dia
        else:
            type = LoaiKhach.nuoc_ngoai

        if not check_cccd(customer["cccd"]):
            cus = KhachHang(ho=customer.get("fname"), ten=customer.get("lname"), cccd=customer.get("cccd"),
                            loai_khach=type, sdt=customer.get("phoneNum"),
                            email=customer.get("email"), dia_chi=customer.get("addr"),
                            user_role=UserRole.khach_hang)
            db.session.add(cus)
            db.session.commit()

    lim = 0
    start = 0
    for room in info["avail_rooms"]:
        for i in range(start, len(customers)):
            if not check_booking_time(get_id_customer_by_cccd(customers[i].get("cccd")),
                                      room, list_to_datetime(info["start_date"]), list_to_datetime(info["end_date"])):
                rent = ThoiGianTraThuePhong(id_khachhang=get_id_customer_by_cccd(customers[i].get("cccd")),
                                            id_phong=room,
                                            thoi_gian_thue=list_to_datetime(info["start_date"]),
                                            thoi_gian_tra=list_to_datetime(info["end_date"]))

                db.session.add(rent)
                db.session.commit()

            lim += 1
            start += 1
            if lim == app.config["CUSTOMER_LIMIT"]:
                lim = 0
                break

    if booker["booker_type"] == "Khách hàng":
        if not check_cccd(booker["cccd"]):
            bker = User(ho=booker.get("fname"), ten=booker.get("lname"), cccd=booker.get("cccd"),
                        sdt=booker.get("phoneNum"), email=booker.get("email"), dia_chi=booker.get("addr"),
                        user_role=UserRole.khach_hang)
            db.session.add(bker)
            db.session.commit()

    for room in info["avail_rooms"]:
        if booker["booker_type"] == "Khách hàng":
            id_user = get_id_user_by_cccd(booker["cccd"])
        else:
            split_name = booker["recep_name"].split(" ")
            fname = "".join(split_name[0: len(split_name) - 1])
            lname = split_name[-1]
            id_user = get_id_user_by_name(fname, lname)

        book_event = NguoiDatPhong(id_user=id_user, id_phong=room,
                                   thoi_gian_dat=datetime.datetime.today())
        db.session.add(book_event)
        db.session.commit()

    return jsonify()  # redirect('/')


if __name__ == "__main__":
    import admin

    app.run(debug=True)
    # with app.app_context():
    #
