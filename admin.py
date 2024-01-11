# from flask_admin.contrib.geoa import ModelView
from flask import redirect
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_login import logout_user, login_required, current_user

from __init__ import admin, db
from models import Phong, KhachHang, UserRole#, PhieuDatPhong, PhieuThuePhong


class StaffModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.NHAN_VIEN


class PhieuDatPhongView(StaffModelView):
    edit_modal = True
    details_modal = True

    column_labels = dict(tenNguoiDat='Tên người đặt', ngayDatPhong='Ngày đặt phòng', ngayTraPhong='Ngày trả phòng',
                         cacPhong='Các phòng')
    form_columns = ('tenNguoiDat', 'ngayDatPhong', 'ngayTraPhong', 'cacPhong')


class PhieuThuePhongView(StaffModelView):
    edit_modal = True
    details_modal = True


class LogoutView(BaseView):
    @expose('/')
    def logout(self):
        logout_user()
        return redirect('/admin/login')


def is_accessible(self):
    return current_user.is_authenticated


class HoaDonThanhToanView(BaseView):
    def __init__(self, name, session):
        self.name = name
        self.session = session
        super(HoaDonThanhToanView, self).__init__(name=name)

    @expose('/')
    def bill(self):
        # data = self.session.query(PhieuThuePhong).all()
        return self.render('/admin/list_bill.html', data=data)


class BaoCaoThangView(BaseView):
    def __init__(self, name, session):
        self.name = name
        self.session = session
        super(BaoCaoThangView, self).__init__(name=name)

    @expose('/')
    def bill(self):
        data = self.session.query(PhieuThuePhong).all()
        return self.render('/admin/BaoCaoThang.html', data=data)


class BaoCaoMatDoView(BaseView):
    def __init__(self, name, session):
        self.name = name
        self.session = session
        super(BaoCaoMatDoView, self).__init__(name=name)

    @expose('/')
    def bill(self):
        data = self.session.query(PhieuThuePhong).all()
        return self.render('/admin/BaoCaoMatDo.html', data=data)


class PhongView(StaffModelView):
    edit_modal = True
    details_modal = True


class KhachHangView(StaffModelView):
    edit_modal = True
    details_modal = True


# admin.add_view(PhieuDatPhongView(PhieuDatPhong, db.session, name="Phiếu Đặt Phòng"))
# admin.add_view(PhieuThuePhongView(PhieuThuePhong, db.session, name="Phiếu Thuê Phòng"))
admin.add_view(PhongView(Phong, db.session, name="Danh sách phòng"))
admin.add_view(KhachHangView(KhachHang, db.session, name="Danh sách khách hàng"))
admin.add_view(LogoutView(name="Đăng xuất"))
admin.add_view(HoaDonThanhToanView(name="Hóa đơn", session=db.session))
admin.add_view(BaoCaoThangView(name="Báo cáo tháng", session=db.session))
admin.add_view(BaoCaoMatDoView(name="Báo cáo mật độ", session=db.session))
