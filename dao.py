from models import *
from __init__ import app, db
import hashlib
from sqlalchemy import or_, and_


def get_all_loai_phong():
    return LoaiPhong.qurey.all()


# def get_all_blogs():
#     return Blog.query.all()
#
#
# def get_blog(blog_id):
#     return Blog.query.filter(Blog.id.contains(blog_id))
#
#
# def get_blog_kw(kw):
#     blogs = Blog.query
#
#     if kw:
#         blogs = blogs.filter(Blog.title.contains(kw))
#
#     return blogs.all()
#
#
# def get_last_message_id():
#     return Message.query.order_by(Message.id.desc()).first()
#
#
# def count_blogs():
#     return Blog.query.count()
#
#
def get_user(user_id):
    return User.get.query(user_id)


#
#
# def get_user_by_name(name):
#     return User.query.filter(User.username.contains(name)).first()
#
#


def auth_user(username, password):
    password = str(hashlib.md5(password.encode("utf-8")).hexdigest())

    return User.query.filter(User.username.__eq__(username),
                             User.password.__eq__(password)).first()


def get_room_type_id(room_type):
    return LoaiPhong.query.filter(LoaiPhong.loai_phong == room_type).first().id


def rooms_by_suite(suite):
    id = get_room_type_id(suite)
    rooms = Phong.query.filter(Phong.id_loaiphong == id).all()
    return [room.id for room in rooms]


def rooms_by_rent_time(suite, checkin, checkout):
    rooms = rooms_by_suite(suite)

    # avail_rooms = ThoiGianTraThuePhong.query.filter(ThoiGianTraThuePhong.id_phong.in_(rooms),
    #                                                 or_(and_(ThoiGianTraThuePhong.thoi_gian_thue >= checkin,
    #                                                          ThoiGianTraThuePhong.thoi_gian_thue >= checkout),
    #                                                     and_(ThoiGianTraThuePhong.thoi_gian_tra <= checkout,
    #                                                          ThoiGianTraThuePhong.thoi_gian_tra <= checkin)
    #                                                     )).all()
    invalid_rooms = ThoiGianTraThuePhong.query.filter(ThoiGianTraThuePhong.id_phong.in_(rooms),
                                                    ThoiGianTraThuePhong.thoi_gian_tra >= checkin,
                                                    ThoiGianTraThuePhong.thoi_gian_thue <= checkout).all()

    invalid_rooms = [room.id_phong for room in invalid_rooms]

    avail_rooms = list(filter(lambda x: x not in invalid_rooms, rooms))
    return avail_rooms


def get_id_customer_by_cccd(cccd):
    return KhachHang.query.filter(KhachHang.cccd.__eq__(cccd)).first().id


def get_id_user_by_cccd(cccd):
    return User.query.filter(User.cccd.__eq__(cccd)).first().id


def get_room_types():
    return [type.loai_phong for type in LoaiPhong.query.all()];


def get_receptionist_names():
    return [rec.ho + " " + rec.ten for rec in LeTan.query.all()]


def check_cccd(cccd):
    avail = User.query.filter(User.cccd == cccd).first()
    if avail:
        return True
    else:
        return False


def get_id_user_by_name(fname, lname):
    return User.query.filter(User.ho == fname, User.ten == lname).first().id


def check_booking_time(id_customer, id_room, start_date, end_date):
    return ThoiGianTraThuePhong.query.filter(ThoiGianTraThuePhong.id_khachhang == id_customer,
                                             ThoiGianTraThuePhong.id_phong == id_room,
                                             ThoiGianTraThuePhong.thoi_gian_thue == start_date,
                                             ThoiGianTraThuePhong.thoi_gian_tra == end_date).first()