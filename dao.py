from models import *
from __init__ import app, db
import hashlib


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


def get_suite_id(suite):
    return LoaiPhong.query.filter(LoaiPhong.loai_phong == suite).first().id


def count_rooms_by_suite(suite):
    id = get_suite_id(suite)
    rooms = Phong.query.filter(Phong.id_loaiphong == id).all()
    return [room.id for room in rooms]


def count_rooms_by_rent_time(suite, checkin, checkout):
    rooms = count_rooms_by_suite(suite)

    return ThoiGianTraThuePhong.query.filter(ThoiGianTraThuePhong.id_phong.in_(rooms),
                                             ThoiGianTraThuePhong.thoi_gian_thue >= checkin,
                                             ThoiGianTraThuePhong.thoi_gian_tra <= checkout).count()


def check_available(suite, checkin, checkout):
    pass