# from flask_admin.contrib.geoa import ModelView
from gettext import gettext

from flask import redirect, flash, url_for, render_template
from flask_admin import BaseView, expose, AdminIndexView
from flask_admin.contrib.sqla import ModelView
from flask_admin.helpers import get_form_data
from flask_login import logout_user, login_required, current_user
from markupsafe import Markup
from sqlalchemy import func

from __init__ import admin, db
from models import *
from dao import *

class StaffModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.quan_ly


class PhieuDatPhongView(StaffModelView):
    edit_modal = True
    details_modal = True

    column_labels = dict(tenNguoiDat='Tên người đặt', ngayDatPhong='Ngày đặt phòng', ngayTraPhong='Ngày trả phòng',
                         cacPhong='Các phòng')
    form_columns = ('tenNguoiDat', 'ngayDatPhong', 'ngayTraPhong', 'cacPhong')


class PhieuDatPhongView(ModelView):
    edit_modal = True
    details_modal = True
    column_list = ['id_user', 'thoi_gian_dat', 'lap_phieu', 'thanh_toan']

    column_labels = {
        'id_user': "Người đặt phòng",
        'thoi_gian_dat': 'Thời gian đặt',
        'lap_phieu': 'Lập phiếu thuê',
        'thanh_toan': 'Thanh toán',
    }


class PhieuThuePhongView(ModelView):
    edit_modal = True
    details_modal = True
    column_list = ['id_user', 'thoi_gian_dat', 'lap_phieu', 'thanh_toan']

    column_labels = {
        'id_user': "Người đặt phòng",
        'thoi_gian_dat': 'Thời gian đặt',
        'lap_phieu': 'Lập phiếu thuê',
        'thanh_toan': 'Thanh toán',
    }

    def _custom_button_formatter(view, context, model, name):
        url = url_for('.get_details')

        _html = '''<form action="{checkout_url}" method="post">
                                <input id="id_user" name="id_user"  type="hidden" value="{id_user}">
                                <input id="thoi_gian_dat" name="thoi_gian_dat"  type="hidden" value="{thoi_gian_dat}">
                                <button class="btn btn-info" type='submit'>Lập phiếu thu</button>
                            </form'''.format(checkout_url=url, id_user=model.id_user, thoi_gian_dat=model.thoi_gian_dat)

        return Markup(_html)

    def _custom_button_formatter_receipt(view, context, model, name):
        url = url_for('.get_receipt')

        _html = '''<form action="{checkout_url}" method="post">
                                <input id="id_user" name="id_user"  type="hidden" value="{id_user}">
                                <input id="thoi_gian_dat" name="thoi_gian_dat"  type="hidden" value="{thoi_gian_dat}">
                                <button class="btn btn-danger" type='submit'>Thanh toán</button>
                            </form'''.format(checkout_url=url, id_user=model.id_user, thoi_gian_dat=model.thoi_gian_dat)

        return Markup(_html)

    column_formatters = {
        'lap_phieu': _custom_button_formatter,
        'thanh_toan': _custom_button_formatter_receipt,
        'id_user': lambda view, context, model, name: get_full_name_by_id(model.id_user),
    }

    column_searchable_list = ['id_user']

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        query = self.get_query()

        if search:
            query = query.filter(func.concat(User.ho, " ", User.ten).ilike(f"%{search}%"))
            # print(query.all())

        return super().get_list(page, sort_column, sort_desc, search, filters, execute, page_size)

    @expose('getDetails', methods=['post'])
    def get_details(self):
        form = get_form_data()
        # print("data 1", form["id_user"])
        return redirect(url_for("get_details", id_user=form["id_user"],
                                thoi_gian_dat=form["thoi_gian_dat"]))

    @expose('getReceipt', methods=['post'])
    def get_receipt(self):
        form = get_form_data()
        # print("data 1", form["id_user"])
        return redirect(url_for("get_receipt", id_user=form["id_user"],
                                thoi_gian_dat=form["thoi_gian_dat"]))

    extra_js = ["/static/js/main.js"]


class LogoutView(BaseView):
    @expose('/')
    def logout(self):
        logout_user()
        return redirect('/login')


def is_accessible(self):
    return current_user.is_authenticated


class HoaDonThanhToanView(ModelView):
    edit_modal = True
    details_modal = True
    column_list = ['id_user', 'thoi_gian_dat', 'lap_phieu', 'thanh_toan']

    column_labels = {
        'id_user': "Người đặt phòng",
        'thoi_gian_dat': 'Thời gian đặt',
        'lap_phieu': 'Lập phiếu thuê',
        'thanh_toan': 'Thanh toán',
    }

    def _custom_button_formatter(view, context, model, name):
        url = url_for('.get_details')

        _html = '''<form action="{checkout_url}" method="post">
                            <input id="id_user" name="id_user"  type="hidden" value="{id_user}">
                            <input id="thoi_gian_dat" name="thoi_gian_dat"  type="hidden" value="{thoi_gian_dat}">
                            <button class="btn btn-info" type='submit'>Lập phiếu thu</button>
                        </form'''.format(checkout_url=url, id_user=model.id_user, thoi_gian_dat=model.thoi_gian_dat)

        return Markup(_html)

    def _custom_button_formatter_receipt(view, context, model, name):
        url = url_for('.get_details')

        _html = '''<form action="{checkout_url}" method="post">
                            <input id="id_user" name="id_user"  type="hidden" value="{id_user}">
                            <input id="thoi_gian_dat" name="thoi_gian_dat"  type="hidden" value="{thoi_gian_dat}">
                            <button class="btn btn-info" type='submit'>Thanh toán</button>
                        </form'''.format(checkout_url=url, id_user=model.id_user, thoi_gian_dat=model.thoi_gian_dat)

        return Markup(_html)

    column_formatters = {
        'lap_phieu': _custom_button_formatter,
        'thanh_toan': _custom_button_formatter_receipt,
        'id_user': lambda view, context, model, name: get_full_name_by_id(model.id_user),
    }

    column_searchable_list = ['id_user']

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        query = self.get_query()

        if search:
            query = query.filter(func.concat(User.ho, " ", User.ten).ilike(f"%{search}%"))
            # print(query.all())

        return super().get_list(page, sort_column, sort_desc, search, filters, execute, page_size)

    @expose('getDetails', methods=['post'])
    def get_details(self):
        form = get_form_data()
        # print("data 1", form["id_user"])
        return redirect(url_for("get_details", id_user=form["id_user"],
                                thoi_gian_dat=form["thoi_gian_dat"]))

    extra_js = ["/static/js/main.js"]


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


admin.add_view(PhieuThuePhongView(NguoiDatPhong, db.session, name="Phiếu Đặt Phòng"))
admin.add_view(PhieuThuePhongView(NguoiDatPhong, db.session, name="Phiếu Thuê Phòng"))
admin.add_view(PhongView(Phong, db.session, name="Danh sách phòng"))
admin.add_view(KhachHangView(KhachHang, db.session, name="Danh sách khách hàng"))
admin.add_view(BaoCaoThangView(name="Báo cáo tháng", session=db.session))
admin.add_view(BaoCaoMatDoView(name="Báo cáo mật độ", session=db.session))
admin.add_view(LogoutView(name="Đăng xuất"))