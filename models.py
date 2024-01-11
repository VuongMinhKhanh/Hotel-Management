from sqlalchemy import Column, Integer, String, DOUBLE, ForeignKey, BOOLEAN, Enum, LargeBinary, DATETIME
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
from __init__ import app, db
from flask_login import UserMixin
import hashlib
import enum
import os
import datetime


class UserRole(enum.Enum):
    khach_hang = 1
    le_tan = 2
    quan_ly = 3


class LoaiKhach(enum.Enum):
    noi_dia = 1
    nuoc_ngoai = 2


class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    username = Column(String(45), unique=True, nullable=True)
    password = Column(String(45), nullable=True)
    ho = Column(String(22), nullable=False)
    ten = Column(String(45), nullable=False)
    gioi_tinh = Column(BOOLEAN, nullable=False, default=False)
    ngay_sinh = Column(DATETIME, nullable=True)
    cccd = Column(String(15), nullable=False, unique=True)
    sdt = Column(String(12))
    email = Column(String(30))
    dia_chi = Column(String(100))
    user_role = Column(Enum(UserRole), default=UserRole.quan_ly)

    def __str__(self):
        return self.name


class KhachHang(User):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    loai_khach = Column(Enum(LoaiKhach), nullable=False, default=LoaiKhach.noi_dia)

    def dat_phong(self):
        pass


class LeTan(User):
    id = Column(Integer, ForeignKey(User.id), primary_key=True, nullable=False)
    luong = Column(DOUBLE, nullable=False, default=1000)
    def cho_thue_phong(self):
        pass


class LoaiPhong(db.Model):
    id = Column(String(10), primary_key=True, nullable=False)
    loai_phong = Column(String(30), nullable=False)
    mo_ta = Column(String(300), default="")
    dien_tich = Column(DOUBLE, nullable=False)
    cac_phong = relationship("Phong", backref="LoaiPhong", lazy=True)

    def __str__(self):
        return self.loai_phong


# tiennghi
class TienNghi(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ten = Column(String(45), nullable=False)
    tinh_trang = Column(BOOLEAN, nullable=False, default=True)
    gia_tien = Column(DOUBLE, nullable=False, default=100)


# loaiphong -- tiennghi
class LoaiPhong_TienNghi(db.Model):
    id_loaiphong = Column(String(10), ForeignKey(LoaiPhong.id), primary_key=True, nullable=False)
    id_tiennghi = Column(Integer, ForeignKey(TienNghi.id), primary_key=True, nullable=False)
    so_luong = Column(Integer, nullable=False, default=1)


# dich vu
class DichVu(db.Model):
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    ten = Column(String(45), nullable=False)
    tinh_trang = Column(BOOLEAN, nullable=False, default=True)
    gia_tien = Column(DOUBLE, nullable=False, default=0)


# loaiphong -- dichvu
class LoaiPhong_DichVu(db.Model):
    id_loaiphong = Column(String(10), ForeignKey(LoaiPhong.id), primary_key=True, nullable=False)
    id_dichvu = Column(Integer, ForeignKey(DichVu.id), primary_key=True, nullable=False)


# PHONG
class Phong(db.Model):
    id = Column(String(10), primary_key=True, nullable=False)
    tinh_trang = Column(BOOLEAN, nullable=False, default=True)
    id_loaiphong = Column(String(45), ForeignKey(LoaiPhong.id), primary_key=True, nullable=False)


# khach hang - phong
class ThoiGianTraThuePhong(db.Model):
    id_khachhang = Column(Integer, ForeignKey(KhachHang.id), nullable=False, primary_key=True)
    id_phong = Column(String(3), ForeignKey(Phong.id), primary_key=True, nullable=False)
    thoi_gian_thue = Column(DATETIME, nullable=False, primary_key=True)
    thoi_gian_tra = Column(DATETIME, nullable=False, primary_key=True)


class NguoiDatPhong(db.Model):
    id_user = Column(Integer, ForeignKey(User.id), nullable=False, primary_key=True)
    id_phong = Column(String(10), ForeignKey(Phong.id), nullable=False, primary_key=True)
    thoi_gian_dat = Column(DATETIME, nullable=False, primary_key=True)


class HoaDon(db.Model):
    id = Column(Integer, primary_key=True, autoincrement=True)


class ChiTietHoaDon(db.Model):
    id_phong = Column(String(10), ForeignKey(Phong.id), nullable=False, primary_key=True)
    id_hoadon = Column(Integer, ForeignKey(HoaDon.id), nullable=False, primary_key=True)
    don_gia = Column(DOUBLE, nullable=False)


# class PhieuDatPhong(db.Model):
#     id = Column(Integer, primary_key=True, autoincrement=True)
#     tenNguoiDat = Column(String(30), nullable=False)
#     ngayDatPhong = Column(DATETIME, nullable=False)
#     ngayTraPhong = Column(DATETIME, nullable=False)
#     cacPhong = relationship('Phong', secondary='ChiTietDatPhong', back_populates='cacPhieuDatPhong')
#
#
# class PhieuThuePhong(db.Model):
#     idPhieu = Column(Integer, primary_key=True, autoincrement=True)
#     idDatPhong = Column(Integer, ForeignKey(PhieuDatPhong.id), unique=True)
#     phieuThuePhong = relationship('PhieuDatPhong')
#
#
# class ChiTietDatPhong(db.Model):
#     idPhong = Column(Integer, ForeignKey(Phong.id), primary_key=True)
#     idPhieuDatPhong = Column(Integer, ForeignKey(PhieuThuePhong.idPhieu), primary_key=True)
#     donGia = Column(Integer, nullable=False)


if __name__ == "__main__":
    with app.app_context():
        r""
        # db.create_all()
        # std = LoaiPhong(id="STD", loai_phong="Standard",
        #                 mo_ta="Là loại phòng cơ bản nhất tại hầu hết các khách sạn, một số khách sạn 5 sao có thể không có loại phòng này. Phòng thường khá nhỏ, được bố trí ở các tầng thấp, không có view đẹp và chỉ gồm những vật dụng cơ bản nhất.",
        #                 dien_tich=15)
        # sup = LoaiPhong(id="SUP", loai_phong="Superior",
        #                 mo_ta="Đây là loại phòng có view nhìn và cách bày trí đẹp mắt hơn hẳn và thường nằm ở những tầng gần giữa của tòa nhà.",
        #                 dien_tich=20)
        # dlx = LoaiPhong(id="DLX", loai_phong="Deluxe",
        #                 mo_ta="Đây là loại phòng nằm ở các tầng giữa trở lên nên sở hữu view nhìn ra quang cảnh bên ngoài khá đẹp. Ở vị trí này, chất lượng phòng được nâng lên mức cao cấp với các tiện nghi hiện đại và tốt nhất",
        #                 dien_tich=30)
        # sut = LoaiPhong(id="SUT", loai_phong="Suite",
        #                 mo_ta="Đây là loại phòng cao cấp nhất trong tất cả các loại phòng khách sạn, thông thường được bố trí ở các tầng cao nhất, sở hữu diện tích phòng cực rộng với đầy đủ tiện nghi như một căn nhà ở và có view nhìn toàn cảnh từ cửa sổ hoặc ban công ra thành phố cực đẹp",
        #                 dien_tich=45)
        # std_2br = LoaiPhong(id="STD_2br", loai_phong="Standard - Giường đôi",
        #                 mo_ta="Là loại phòng cơ bản nhất tại hầu hết các khách sạn, một số khách sạn 5 sao có thể không có loại phòng này. Phòng thường khá nhỏ, được bố trí ở các tầng thấp, không có view đẹp và chỉ gồm những vật dụng cơ bản nhất.",
        #                 dien_tich=18)
        # sup_2br = LoaiPhong(id="SUP_2br", loai_phong="Superior - Giường đôi",
        #                 mo_ta="Đây là loại phòng có view nhìn và cách bày trí đẹp mắt hơn hẳn và thường nằm ở những tầng gần giữa của tòa nhà.",
        #                 dien_tich=23)
        # db.session.add_all([std, sup, dlx, sut, std_2br, sup_2br])
        # db.session.commit()
        #
        # table = TienNghi(ten="Bàn", gia_tien=300)
        # single_bed = TienNghi(ten="Giường đơn", gia_tien=1000)
        # double_bed = TienNghi(ten="Giường đôi", gia_tien=1500)
        # AC = TienNghi(ten="Máy điều hòa", gia_tien=800)
        # wardrobe = TienNghi(ten="Tủ đồ", gia_tien=1000)
        # TV = TienNghi(ten="TV", gia_tien=200)
        # fridge = TienNghi(ten="Tủ lạnh", gia_tien=1000)
        # pool = TienNghi(ten="Hồ bơi", gia_tien=10000)
        # wifi = TienNghi(ten="Wifi", gia_tien=100)
        # lamp = TienNghi(ten="Đèn bàn", gia_tien=50)
        # beach_view = TienNghi(ten="View biển", gia_tien=7000)
        # toilet = TienNghi(ten="Nhà vệ sinh", gia_tien=500)
        # ornament = TienNghi(ten="Đồ trang trí", gia_tien=5000)
        #
        # db.session.add_all([table, single_bed, double_bed,AC, wardrobe,
        #                     TV, fridge, pool, wifi, lamp, beach_view,toilet, ornament])
        # db.session.commit()
        #
        # std_1 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=1)
        # std_2 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=2)
        # std_3 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=4)
        # std_4 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=5)
        # # std_5 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=6)
        # std_6 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=7)
        # # std_7 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=9)
        # std_8 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=10)
        # std_9 = LoaiPhong_TienNghi(id_loaiphong="STD", id_tiennghi=12)
        #
        # std_2br_1 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=1)
        # std_2br_2 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=3)
        # std_2br_3 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=4)
        # std_2br_4 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=5)
        # # std_2br_5 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=6)
        # std_2br_6 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=7)
        # # std_2br_7 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=9)
        # std_2br_8 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=10)
        # std_2br_9 = LoaiPhong_TienNghi(id_loaiphong="STD_2br", id_tiennghi=12)
        #
        # sup_1 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=1, so_luong=2)
        # sup_2 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=2)
        # sup_3 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=4)
        # sup_4 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=5)
        # # sup_5 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=6)
        # sup_6 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=7)
        # # sup_7 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=9)
        # sup_8 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=10, so_luong=2)
        # sup_9 = LoaiPhong_TienNghi(id_loaiphong="SUP", id_tiennghi=12)
        #
        # sup_2br_1 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=1, so_luong=2)
        # sup_2br_2 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=3)
        # sup_2br_3 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=4)
        # sup_2br_4 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=5)
        # # sup_2br_5 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=6)
        # sup_2br_6 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=7)
        # # sup_2br_7 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=9)
        # sup_2br_8 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=10, so_luong=2)
        # sup_2br_9 = LoaiPhong_TienNghi(id_loaiphong="SUP_2br", id_tiennghi=12)
        #
        # dlx_1 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=1, so_luong=3)
        # dlx_2 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=3, so_luong=2)
        # dlx_3 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=4, so_luong=2)
        # dlx_4 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=5, so_luong=2)
        # # dlx_5 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=6)
        # dlx_6 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=7, so_luong=2)
        # # dlx_7 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=9)
        # dlx_8 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=10, so_luong=3)
        # dlx_9 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=12)
        # dlx_10 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=13)
        # dlx_11 = LoaiPhong_TienNghi(id_loaiphong="DLX", id_tiennghi=11)
        #
        # sut_1 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=1, so_luong=4)
        # sut_2 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=3, so_luong=3)
        # sut_3 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=4, so_luong=3)
        # sut_4 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=5, so_luong=3)
        # # sut_5 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=6)
        # sut_6 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=7, so_luong=2)
        # # sut_7 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=9)
        # sut_8 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=10, so_luong=4)
        # sut_9 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=12)
        # sut_10 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=13)
        # sut_11 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=11)
        # sut_12 = LoaiPhong_TienNghi(id_loaiphong="SUT", id_tiennghi=8)
        #
        # db.session.add_all([std_1, std_2, std_3, std_4, std_6, std_8, std_9,
        #                     std_2br_1, std_2br_2, std_2br_3, std_2br_4, std_2br_6, std_2br_8, std_2br_9,
        #                     sup_1, sup_2, sup_3, sup_4, sup_6, sup_8, sup_9,
        #                     sup_2br_1, sup_2br_2, sup_2br_3, sup_2br_4, sup_2br_6, sup_2br_8, sup_2br_9,
        #                     dlx_1, dlx_2, dlx_3, dlx_4, dlx_6, dlx_8, dlx_9, dlx_10, dlx_11,
        #                     sut_1, sut_2, sut_12, sut_11, sut_9, sut_10, sut_8, sut_6, sut_4, sut_3])
        # db.session.commit()
        #
        # srv1 = DichVu(ten="Bơi", gia_tien=100)
        # srv2 = DichVu(ten="Buffet", gia_tien=300)
        # srv3 = DichVu(ten="Message", gia_tien=250)
        # srv4 = DichVu(ten="Mì tôm", gia_tien=30)
        # srv5 = DichVu(ten="Giặt ủi", gia_tien=100)
        # srv6 = DichVu(ten="Đưa đón sân bay", tinh_trang=0, gia_tien=400)
        #
        # db.session.add_all([srv1, srv6, srv5, srv4, srv3, srv2])
        # db.session.commit()
        #
        # p101 = Phong(id="101", id_loaiphong="STD")
        # p102 = Phong(id="102", id_loaiphong="STD")
        # p103 = Phong(id="103", id_loaiphong="STD_2br")
        #
        # p201 = Phong(id="201", id_loaiphong="SUP")
        # p202 = Phong(id="202", id_loaiphong="SUP_2br")
        # p203 = Phong(id="203", id_loaiphong="SUP_2br")
        #
        # p301 = Phong(id="301", id_loaiphong="DLX")
        # p401 = Phong(id="401", id_loaiphong="SUT")
        #
        # db.session.add_all([p301, p401, p201, p202, p203, p101, p103, p102])
        # db.session.commit()
        #
        # time = datetime.datetime(year=2003, month=6, day=19)
        # us1 = KhachHang(ho="Trần Thanh", ten="Hoàng", ngay_sinh=time.date(), cccd="07228311", user_role=UserRole.khach_hang)
        # time = datetime.datetime(year=2023, month=9, day=2)
        # us2 = LeTan(ho="Vương Minh", ten="Khánh", ngay_sinh=time.date(), cccd="07920302", luong=5000, user_role=UserRole.le_tan)
        # time = datetime.datetime(year=2003, month=1, day=1)
        # us3 = KhachHang(ho="Huỳnh Duy", ten="Đông", ngay_sinh=time.date(), cccd="0123456", user_role=UserRole.khach_hang)
        # admin = User(username='admin', password=hashlib.md5('123'.encode('utf-8')).hexdigest(), ten='admin', ho='admin',
        #              gioi_tinh=True, cccd="123", user_role=UserRole.quan_ly)
        # db.session.add(admin)
        # db.session.commit()
        # db.session.add_all([us1, us2, us3])
        # db.session.commit()
        #
        # cki = datetime.datetime(year=datetime.datetime.today().year, month=1, day=8)
        # cko = datetime.datetime(year=datetime.datetime.today().year, month=1, day=10)
        # rent1 = ThoiGianTraThuePhong(id_khachhang=1, id_phong="103", thoi_gian_thue=cki, thoi_gian_tra=cko)
        # cki = datetime.datetime(year=datetime.datetime.today().year, month=2, day=18)
        # cko = datetime.datetime(year=datetime.datetime.today().year, month=2, day=22)
        # rent2 = ThoiGianTraThuePhong(id_khachhang=1, id_phong="301", thoi_gian_thue=cki, thoi_gian_tra=cko)
        # cki = datetime.datetime(year=datetime.datetime.today().year, month=2, day=1)
        # cko = datetime.datetime(year=datetime.datetime.today().year, month=2, day=13)
        # rent3 = ThoiGianTraThuePhong(id_khachhang=1, id_phong="301", thoi_gian_thue=cki, thoi_gian_tra=cko)
        # db.session.add_all([rent1, rent2, rent3])
        # db.session.commit()
        #
        # booker1 = NguoiDatPhong(id_user=1, id_phong="103", thoi_gian_dat=datetime.datetime.today())
        # booker2 = NguoiDatPhong(id_user=2, id_phong="301", thoi_gian_dat=datetime.datetime.today())
        # booker3 = NguoiDatPhong(id_user=3, id_phong="301", thoi_gian_dat=datetime.datetime.today())
        # db.session.add_all([booker1, booker2, booker3])
        # db.session.commit()