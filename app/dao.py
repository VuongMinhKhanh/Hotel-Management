from models import *
from __init__ import app, db
import hashlib
from sqlalchemy import or_, and_, func, text, cast


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


def get_booking_time(id_khachhang):
    result_dicts = [obj.__dict__ for obj in
                    ThoiGianTraThuePhong.query.filter(ThoiGianTraThuePhong.id_khachhang == int(id_khachhang)).all()]
    return [{k: v for k, v in d.items() if not k.startswith('_')} for d in result_dicts]


def get_full_name_by_id(id_user):
    return User.full_name(User.query.filter(User.id == id_user).first())


def get_last_id_user_in_booking_event():
    return PhieuDatThuePhong.query.order_by(PhieuDatThuePhong.id_datphong.desc()).first().id_datphong


def check_foreigner(room, start_date, end_date):
    customers_id = [cus.id_khachhang for cus in ThoiGianTraThuePhong.query.filter_by(id_phong=room,
                                                                                     thoi_gian_thue=start_date,
                                                                                     thoi_gian_tra=end_date).all()]

    for id in customers_id:
        region = KhachHang.query.filter_by(id=id).first().loai_khach
        if region == LoaiKhach.nuoc_ngoai:
            return True

    return False


def get_id_room_type(room):
    room = str(room)
    return Phong.query.filter_by(id=room).first().id_loaiphong


def get_price(id_room_type):
    convens = [id.id_tiennghi for id in LoaiPhong_TienNghi.query.filter_by(id_loaiphong=id_room_type).all()]
    qtt = [id.so_luong for id in LoaiPhong_TienNghi.query.filter_by(id_loaiphong=id_room_type).all()]
    # print("convens", convens)
    price = 0.0
    for i in range(len(convens)):
        conven_price = TienNghi.query.filter_by(id=convens[i]).first().gia_tien
        # print("gia tien", conven_price, "qtt", qtt[i])
        price += conven_price * qtt[i]

    return price


def is_paid(id_datphong):
    print("hoa don", HoaDon.query.filter_by(id_datphong=id_datphong).first() is not None)
    if HoaDon.query.filter_by(id_datphong=id_datphong).first() is not None:
        return True
    else:
        return False


def count_products_by_cate():
    return db.session.query(TienNghi.id, TienNghi.ten, func.count(TienNghi.id))


def stats_sale(from_date, to_date):
    stats_data = (db.session.query(Phong.id_loaiphong,
                                   cast(func.sum(HoaDon.tien_tong).label(''), Integer),
                                   func.count(HoaDon.id_datphong))
                  .select_from(Phong)
                  .join(ThoiGianTraThuePhong, ThoiGianTraThuePhong.id_phong == Phong.id)
                  .join(PhieuDatThuePhong)
                  .join(HoaDon)
                  .group_by(Phong.id_loaiphong)
                  .filter(ThoiGianTraThuePhong.thoi_gian_tra.between(from_date, to_date))
                  .all())

    print("stat", stats_data)
    return [{'loai_phong': loai_phong, 'doanh_thu': doanh_thu, 'luot_thue': luot_thue}
            for loai_phong, doanh_thu, luot_thue in stats_data]


def stats_mat_do(from_date, to_date):
    stats_data = (db.session.query(Phong.id,
                                   cast(func.sum(func.datediff(ThoiGianTraThuePhong.thoi_gian_tra,
                                                          ThoiGianTraThuePhong.thoi_gian_thue
                                                          )).label(''), Integer))
                  .select_from(Phong)
                  .join(ThoiGianTraThuePhong, ThoiGianTraThuePhong.id_phong == Phong.id)
                  .join(PhieuDatThuePhong)
                  .group_by(Phong.id)
                  .filter(ThoiGianTraThuePhong.thoi_gian_tra.between(from_date, to_date))
                  .all())

    print("stats", stats_data)
    return [{'ma_phong': ma_phong, 'so_ngay_thue': (so_ngay_thue)}
            for ma_phong, so_ngay_thue in stats_data]


def get_customer_limit_value():
    return int(QuyDinh.query.filter_by(regulation=RegulationEnum.customer_limit.name).first().value)


def get_customer_extras_value():
    return QuyDinh.query.filter_by(regulation=RegulationEnum.customer_extras.name).first().value


def get_foreigner_extras_value():
    return QuyDinh.query.filter_by(regulation=RegulationEnum.foreigner_extras.name).first().value