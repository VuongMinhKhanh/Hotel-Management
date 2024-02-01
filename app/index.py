import json
import math
from flask import render_template, request, redirect, jsonify, session, flash, url_for, Response
from flask_admin import expose
from flask_admin.helpers import get_form_data
from flask_admin.babel import gettext
from flask import session as login_session
import os
import base64
from io import BytesIO
import send_file
from send_file import *
from sqlalchemy.orm import class_mapper

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

    return render_template("index.html", suites=suites,
                           # , pages=math.ceil(num/page_size)
                           current_user=current_user)


@login.user_loader
def load_user(user_id):
    return db.session.get(User, user_id)


@app.route("/admin/login", methods=["post"])
def login_admin():
    username = request.form.get("username")
    password = request.form.get("password")

    user = auth_user(username=username, password=password)
    print(user)
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


@app.route('/booking', methods=["get"])
def booking():
    return render_template('booking.html', room_types=get_room_types(),
                           receptionists=get_receptionist_names())


@app.route('/booking_2', methods=["get", 'post'])
def booking_2():
    # if request.method.__eq__('POST'):
    #     return redirect("/booking")
    return render_template('booking_2.html')


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
            if len(bkinfo.get("info").get("avail_rooms")) * get_customer_limit_value() < len(customers):
                return jsonify(False)

    all_customers = []
    for customer in customers:
        all_customers.append(customer)

    for bkinfo in booking_info:
        if bkinfo.get("customers"):
            keys_to_remove = ['customers', 'booker']
            booking_info = [item for item in booking_info if all(key not in item for key in keys_to_remove)]

    booking_info.append({"customers": all_customers})
    print("booker", (booker))
    if bool(booker):
        booking_info.append({"booker": booker})
    else:
        booking_info.append({"booker": {
            "full_name": current_user.ho + " " + current_user.ten,
            "booker_type": "Lễ tân"
        }})

    session['booking_info'] = booking_info
    print("booking info:", booking_info)
    return jsonify(booking_info)


@app.route('/api/bookrooms', methods=['post'])
def confirm_booking():
    booking_info = session.get('booking_info')
    info = next((item['info'] for item in booking_info if 'info' in item), {})
    booker = next((item['booker'] for item in booking_info if 'booker' in item), {})
    customers = next((item['customers'] for item in booking_info if 'customers' in item), [])

    # print(info) # {'avail_rooms': ['301'], 'end_date': ['2024', '01', '10'], 'room_type': 'Deluxe', 'start_date': ['2024', '01', '10']}
    # print(info["avail_rooms"]) # ['301']

    # start adding information to db
    # add customers
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

    # add booker as a non-recep
    print(booker["booker_type"])
    if booker["booker_type"] == "Khách hàng":
        if not check_cccd(booker["cccd"]):
            bker = User(ho=booker.get("fname"), ten=booker.get("lname"), cccd=booker.get("cccd"),
                        sdt=booker.get("phoneNum"), email=booker.get("email"), dia_chi=booker.get("addr"),
                        user_role=UserRole.khach_hang)
            db.session.add(bker)
            db.session.commit()

    # add booking info
    for room in info["avail_rooms"]:
        if booker["booker_type"] == "Khách hàng":
            id_user = get_id_user_by_cccd(booker["cccd"])

        else:
            id_user = current_user.id

        book_event = PhieuDatThuePhong(id_user=id_user,
                                   thoi_gian_dat=datetime.datetime.today())
        db.session.add(book_event)
        db.session.commit()
    id_datphong = get_last_id_user_in_booking_event()



    # add customers to rooms
    lim = 0
    start = 0
    for room in info["avail_rooms"]:
        for i in range(start, len(customers)):
            if not check_booking_time(get_id_customer_by_cccd(customers[i].get("cccd")),
                                      room, list_to_datetime(info["start_date"]), list_to_datetime(info["end_date"])):
                rent = ThoiGianTraThuePhong(id_khachhang=get_id_customer_by_cccd(customers[i].get("cccd")),
                                            id_phong=room,
                                            thoi_gian_thue=list_to_datetime(info["start_date"]),
                                            thoi_gian_tra=list_to_datetime(info["end_date"]),
                                            id_datphong=id_datphong)

                db.session.add(rent)
                db.session.commit()

            lim += 1
            start += 1
            if lim == get_customer_limit_value():
                lim = 0
                break
    return jsonify()


@app.route("/api/send_emails", methods=["post"])
def send_emails():
    data = request.get_json()
    emails = data.get('emails')
    # title = data.get("title")
    # message = data.get("message")
    path = data.get("path")
    # print(emails, message)
    send_files(emails, path)
    return jsonify()


@app.route("/getDetails", methods=["get"])
def get_details():
    id_user = request.args.get("id_user")
    thoi_gian_dat = request.args.get("thoi_gian_dat")
    lastpoint = request.args.get("lastpoint")
    # print("data", id_phong, id_user, thoi_gian_dat)
    # Process the data as needed
    nguoi_dat_phong = PhieuDatThuePhong.query.filter_by(id_user=id_user,
                                                    thoi_gian_dat=thoi_gian_dat).first()

    booker_event = row_to_dict(nguoi_dat_phong)
    booker = row_to_dict(User.query.filter_by(id=booker_event["id_user"]).first())

    dat_phong = ThoiGianTraThuePhong.query.filter_by(id_datphong=booker_event["id_datphong"]).all()
    booking_time = []

    for bk in dat_phong:
        booking_time.append(row_to_dict(bk))
        # print("booking_time", row_to_dict(bk))

    temp_room = []
    for room in booking_time:
        temp_room.append(room["id_phong"])

    temp_room = list(set(temp_room))

    rooms = temp_room[0]

    for i in range(1, len(temp_room)):
        rooms += ", " + temp_room[i]

    customers = []
    for bk in booking_time:
        customer = KhachHang.query.filter_by(id=bk["id_khachhang"]).first()
        customers.append(row_to_dict(customer))

    return render_template("details_template.html", booker=booker,
                           rooms=rooms, booking_time=booking_time,
                           customers=customers, noi_dia=LoaiKhach.noi_dia, lastpoint=lastpoint)


def row_to_dict(row):
    data = {}
    for column in class_mapper(row.__class__).mapped_table.columns:
        data[column.name] = getattr(row, column.name)
    return data


@app.route("/getReceipt", methods=["get"])
def get_receipt():
    id_user = request.args.get("id_user")
    thoi_gian_dat = request.args.get("thoi_gian_dat")

    receipt = session.get("receipt")
    if receipt is None:
        receipt = {}

    # print("data", id_phong, id_user, thoi_gian_dat)
    # Process the data as needed
    nguoi_dat_phong = PhieuDatThuePhong.query.filter_by(id_user=id_user,
                                                    thoi_gian_dat=thoi_gian_dat).first()

    booker_event = row_to_dict(nguoi_dat_phong)
    booker = row_to_dict(User.query.filter_by(id=booker_event["id_user"]).first())

    dat_phong = ThoiGianTraThuePhong.query.filter_by(id_datphong=booker_event["id_datphong"]).all()
    booking_time = []

    for bk in dat_phong:
        booking_time.append(row_to_dict(bk))
        # print("booking_time", row_to_dict(bk))

    temp_room = []
    for room in booking_time:
        temp_room.append(room["id_phong"])

    # get frequency of rooms
    room_info = []

    for items in temp_room:
        freq = {"phong": items, "so_luong": temp_room.count(items),
                "nuoc_ngoai": check_foreigner(int(items), booking_time[0]["thoi_gian_thue"],
                                              booking_time[0]["thoi_gian_tra"])}
        # print("freq", freq)
        room_info.append(freq)

    # remove dupes
    res_list = []
    for i in range(len(room_info)):
        if room_info[i] not in room_info[i + 1:]:
            res_list.append(room_info[i])

    room_info = res_list
    # print("room_info", room_info)

    # get price
    # print("số ngày", (booking_time[0]["thoi_gian_tra"] - booking_time[0]["thoi_gian_thue"]).days)
    days = (booking_time[0]["thoi_gian_tra"] - booking_time[0]["thoi_gian_thue"]).days
    for room in room_info:
        # print("room_type", get_id_room_type(list(room.keys())[0]))
        # print("price", get_price(get_id_room_type(room["phong"])))
        price = get_price(get_id_room_type(room["phong"]))
        price = (price
                 * (int(room["so_luong"] + get_customer_extras_value() * int(
                    room["so_luong"] == get_customer_limit_value()))
                    * (1 + (get_foreigner_extras_value() * int(room["nuoc_ngoai"])))
                    * days)) * 1000

        str_price = "{:,}".format(price)

    # print("final price", final_price)
    # get room's names
    temp_room = list(set(temp_room))

    rooms = temp_room[0]

    for i in range(1, len(temp_room)):
        rooms += ", " + temp_room[i]

    # print("booker", (booker))
    receipt = {
        "id_datphong": booker_event["id_datphong"],  # id_phieudat
        "tong_tien": price,
        "booker_full_name": booker["ho"] + " " + booker["ten"],
        "rooms": rooms,
        "booking_time": booking_time,
        "str_price": str_price
    }
    # print("form", compose_receipt_file(receipt))
    session["receipt"] = receipt
    return render_template("receipt.html", booker=booker,
                           rooms=rooms, booking_time=booking_time, price=str_price,
                           is_paid=is_paid(receipt["id_datphong"]))


@app.route("/api/pay", methods=["post"])
def pay():
    receipt = session.get("receipt")

    print((receipt["tong_tien"]))

    bill = HoaDon(id_datphong=receipt["id_datphong"], tien_tong=receipt["tong_tien"])
    db.session.add(bill)
    db.session.commit()

    return jsonify(receipt)


@app.route('/api/baocaodoanhthu', methods=['GET'])
def stats_sale():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    return dao.stats_sale(from_date, to_date)


@app.route('/api/baocaomatdo', methods=['GET'])
def stats_mat_do():
    from_date = request.args.get('from_date')
    to_date = request.args.get('to_date')
    return dao.stats_mat_do(from_date, to_date)


@app.route('/api/save_form_image', methods=['POST'])
def save_form_image():
    # print("start saving")
    data = request.get_json()
    receipt = session.get("receipt")
    img_data = data['imgData']

    # Remove the header from the data URL
    header, encoded = img_data.split(",", 1)
    data = base64.b64decode(encoded)

    # Save the image to a file
    # receipt_form = f"forms\\receipt_form_capture.png"
    receipt_form = f"forms\\{receipt['booker_full_name']}_{receipt['booking_time'][0]['thoi_gian_thue'].strftime('%Y-%m-%d')}_{receipt['booking_time'][0]['thoi_gian_tra'].strftime('%Y-%m-%d')}_Hóa Đơn.png"
    # receipt_form = f"forms\\{receipt['booker_full_name']}.png"

    with open(receipt_form, 'wb') as file:
        file.write(data)

    # print("end saving")
    return jsonify(receipt_form)


if __name__ == "__main__":
    import admin

    app.run(debug=True)
    # with app.app_context():
        # print(os.path.abspath(""))
        # print(os.remove("forms\Lễ Tên.png"))
    #     form = f'''<form method="post" id="receipt">
    #             <h2 class="text-center">HÓA ĐƠN THANH TOÁN</h2>
    #             <div class="mt-1 mb-1">
    #                 <div class="row g-3 d-flex align-items-center justify-content-center">
    #                     <div class="col-md-6">
    #                         <div class="form-floating">
    #                             <input id="room_type" class="form-control" type="text" style="background: white"
    #                                    value="401" disabled>
    #                             <label>Các phòng thuê</label>
    #                         </div>
    #                     </div>
    #                     <div class="col-md-6">
    #                         <div class="form-floating">
    #                             <input id="room_quantity" class="form-control" type="text" style="background: white"
    #                                    value="Vương Minh Khánh" disabled>
    #                             <label class="" for="">Người đặt phòng</label>
    #                         </div>
    #                     </div>
    #                     <div class="col-md-6">
    #                         <div class="form-floating date" id="date3" data-target-input="nearest">
    #                             <input id="checkin" class="form-control" type="text" style="background: white"
    #                                    value="2024-02-09 00:00:00" disabled>
    #                             <label for="checkin">Ngày nhận phòng</label>
    #                         </div>
    #                     </div>
    #                     <div class="col-md-6">
    #                         <div class="form-floating date" id="date4" data-target-input="nearest">
    #                             <input id="checkout" class="form-control" type="text" style="background: white"
    #                                    value="2024-02-10 00:00:00" disabled>
    #                             <label for="checkout"> Ngày trả phòng</label>
    #                         </div>
    #                     </div>
    #                     <div class="col-md-2">
    #                         <div class="form-floating">
    #                             <h2>Tổng tiền</h2>
    #                         </div>
    #                     </div>
    #                     <div class="col-md-10">
    #                         <div class="">
    #                             <h2 id="room_type" class=" text-danger text-center bg-white "
    #                                 style="font-size: 3em">89,500,000.0 VND</h2>
    #                         </div>
    #                     </div>
    #                 </div>
    #             </div>
    #         </form>'''


