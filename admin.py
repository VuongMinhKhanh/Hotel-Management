# from flask_admin.contrib.geoa import ModelView
from gettext import gettext
from flask import redirect, flash, url_for, render_template, request
from flask_admin import BaseView, expose, AdminIndexView, Admin
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla import ModelView, view
from flask_admin.contrib.sqla.fields import QuerySelectField
from flask_admin.form import Select2Widget
from flask_admin.helpers import get_form_data
from flask_login import logout_user, login_required, current_user
from markupsafe import Markup
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from wtforms import SelectField
from wtforms.validators import DataRequired

from __init__ import db, admin
from models import *
from dao import *


#
# class MyAdmin(AdminIndexView):
#     @expose('/')
#     def index(self):
#         return self.render('admin/index.html', stats=count_products_by_cate())
#
#
# admin = Admin(app=app, name='QUẢN TRỊ KHÁCH SẠN', template_mode='bootstrap4', index_view=MyAdmin())


class AdminModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.quan_ly


class ReceptionistModelView(ModelView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.le_tan


class AdminBaseView(BaseView):
    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.quan_ly


class PhieuDatPhongView(ReceptionistModelView):
    edit_modal = True
    details_modal = True
    column_list = ['id_user', 'thoi_gian_dat', 'lap_phieu_dat', 'cho_thue_phong']

    column_labels = {
        'id_user': "Người đặt phòng",
        'thoi_gian_dat': 'Thời gian đặt',
        'lap_phieu_dat': 'Xem phiếu đặt',
        'cho_thue_phong': 'Cho thuê phòng',
    }

    def get_query(self):
        return self.session.query(self.model).filter(self.model.cho_thue == False)

    @staticmethod
    def _custom_button_formatter(view, context, model, name, button_name, button_type):
        url = url_for('.' + name)
        _html = f'''
                    <form action="{url}" method="post">
                        <input id="id_user" name="id_user" type="hidden" value="{model.id_user}">
                        <input id="thoi_gian_dat" name="thoi_gian_dat" type="hidden" value="{model.thoi_gian_dat}">
                        <button class="btn btn-{button_type} " type='submit'>{button_name}</button>
                    </form>
                '''
        return Markup(_html)

    column_formatters = {
        'lap_phieu_dat': lambda view, context, model, name: PhieuThuePhongView._custom_button_formatter(view, context,
                                                                                                        model,
                                                                                                        'get_details',
                                                                                                        '&#9432;',
                                                                                                        'info'),
        'cho_thue_phong': lambda view, context, model, name: PhieuThuePhongView._custom_button_formatter(view, context,
                                                                                                         model,
                                                                                                         'change_to_rent',
                                                                                                         '&#10003;',
                                                                                                         'success'),
        'id_user': lambda view, context, model, name: get_full_name_by_id(model.id_user),
    }

    @expose('getDetails', methods=['post'])
    def get_details(self):
        form = get_form_data()
        # print("Url", url_for("phieudatphong.index_view"))
        # print("data 1", form["id_user"])
        return redirect(url_for("get_details", id_user=form["id_user"],
                                thoi_gian_dat=form["thoi_gian_dat"], lastpoint="booking_form"))

    @expose('changeToRent', methods=['post'])
    def change_to_rent(self):
        form = get_form_data()
        booker = get_full_name_by_id(form["id_user"])
        flash(gettext(f"Đã chuyển phiếu đặt của -{booker}- thành phiếu thuê!"), "success")

        # print("query", PhieuDatThuePhong.query.filter_by(id_user=form["id_user"], thoi_gian_dat=form["thoi_gian_dat"]).first().id_user)
        # PhieuDatThuePhong.query.filter_by(id_user=form["id_user"], thoi_gian_dat=form["thoi_gian_dat"]).update({PhieuDatThuePhong.cho_thue: True},
        #                                                                   synchronize_session="fetch")

        booking_info = PhieuDatThuePhong.query.filter_by(id_user=form["id_user"],
                                                         thoi_gian_dat=form["thoi_gian_dat"]).first()
        booking_info.cho_thue = True
        db.session.commit()

        # print("data 1", form["id_user"])
        # return redirect(url_for("get_details", id_user=form["id_user"],
        #                         thoi_gian_dat=form["thoi_gian_dat"]))
        return redirect(url_for('.index_view'))

    column_searchable_list = ['id_user']

    def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
        query = self.get_query()
        # print("self", self.column_searchable_list)
        # Apply filters if provided
        if filters:
            query = self.apply_filters(query, filters)

        if search:
            # If search term is provided, modify the query to search by the full name
            search_term = f"%{search}%"
            # This could be a subquery that gets full names from user IDs
            full_name_query = self.session.query(User.id.label('id_user'),
                                                 func.concat(User.ho, ' ', User.ten).label('full_name')).subquery()
            # print("full name query", full_name_query)
            query = query.join(full_name_query, PhieuDatThuePhong.id_user == full_name_query.c.id_user)
            query = query.filter(full_name_query.c.full_name.ilike(search_term))

        # Execute the modified query and get the list
        count_query = self.get_count_query()
        return super(PhieuDatPhongView, self).get_list(page, sort_column, sort_desc, search, filters, execute,
                                                       page_size)


class PhieuThuePhongView(ReceptionistModelView):
    edit_modal = True
    details_modal = True
    column_list = ['id_user', 'thoi_gian_dat', 'lap_phieu', 'thanh_toan']

    column_labels = {
        'id_user': "Người đặt phòng",
        'thoi_gian_dat': 'Thời gian đặt',
        'lap_phieu': 'Xem phiếu thuê',
        'thanh_toan': 'Xem hóa đơn',
    }

    def get_query(self):
        return self.session.query(self.model).filter(self.model.cho_thue == True)

    @staticmethod
    def _custom_button_formatter(view, context, model, name, button_name, button_type):
        url = url_for('.' + name)
        if name == "get_receipt":
            id_datphong = PhieuDatThuePhong.query.filter_by(id_user=model.id_user,
                                                            thoi_gian_dat=model.thoi_gian_dat
                                                            ).first().id_datphong
            if is_paid(id_datphong):
                button_type = "success"
                button_name = "&#xe8b0;"

        _html = f'''
                <form action="{url}" method="post">
                    <input id="id_user" name="id_user" type="hidden" value="{model.id_user}">
                    <input id="thoi_gian_dat" name="thoi_gian_dat" type="hidden" value="{model.thoi_gian_dat}">
                    <button class="btn btn-{button_type}" type='submit'>{button_name}</button>
                </form>
            '''
        return Markup(_html)

    column_formatters = {
        'lap_phieu': lambda view, context, model, name: PhieuThuePhongView._custom_button_formatter(view, context,
                                                                                                    model,
                                                                                                    'get_details',
                                                                                                    '&#9432;',
                                                                                                    'info'),
        'thanh_toan': lambda view, context, model, name: PhieuThuePhongView._custom_button_formatter(view, context,
                                                                                                     model,
                                                                                                     'get_receipt',
                                                                                                     '&#36;',
                                                                                                     'danger'),
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
                                thoi_gian_dat=form["thoi_gian_dat"], lastpoint="renting_form"))

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
#
#
# class HoaDonThanhToanView(ReceptionistModelView):
#     can_view_details = True
#     edit_modal = True
#     details_modal = True
#
#     column_list = ['id_user', 'thoi_gian_dat', 'lap_phieu', 'thanh_toan']
#
#     column_labels = {
#         'id_user': "Người đặt phòng",
#         'thoi_gian_dat': 'Thời gian đặt',
#         'lap_phieu': 'Lập phiếu thuê',
#         'thanh_toan': 'Thanh toán',
#     }
#
#     def _custom_button_formatter(view, context, model, name, label):
#         url = url_for('.get_details')
#
#         _html = '''<form action="{checkout_url}" method="post">
#                             <input id="id_user" name="id_user"  type="hidden" value="{id_user}">
#                             <input id="thoi_gian_dat" name="thoi_gian_dat"  type="hidden" value="{thoi_gian_dat}">
#                             <button class="btn btn-info" type='submit'>{ label }</button>
#                         </form'''.format(checkout_url=url, id_user=model.id_user, thoi_gian_dat=model.thoi_gian_dat)
#
#         return Markup(_html)
#
#     def _custom_button_formatter_receipt(view, context, model, name):
#         url = url_for('.get_details')
#
#         _html = '''<form action="{checkout_url}" method="post">
#                             <input id="id_user" name="id_user"  type="hidden" value="{id_user}">
#                             <input id="thoi_gian_dat" name="thoi_gian_dat"  type="hidden" value="{thoi_gian_dat}">
#                             <button class="btn btn-info" type='submit'>Thanh toán</button>
#                         </form'''.format(checkout_url=url, id_user=model.id_user, thoi_gian_dat=model.thoi_gian_dat)
#
#         return Markup(_html)
#
#     column_formatters = {
#         'lap_phieu': _custom_button_formatter,
#         'thanh_toan': _custom_button_formatter_receipt,
#         'id_user': lambda view, context, model, name: get_full_name_by_id(model.id_user),
#     }
#
#     column_searchable_list = ['id_user']
#
#     def get_list(self, page, sort_column, sort_desc, search, filters, execute=True, page_size=None):
#         query = self.get_query()
#
#         if search:
#             query = query.filter(func.concat(User.ho, " ", User.ten).ilike(f"%{search}%"))
#             # print(query.all())
#
#         return super().get_list(page, sort_column, sort_desc, search, filters, execute, page_size)
#
#     @expose('getDetails', methods=['post'])
#     def get_details(self):
#         form = get_form_data()
#         # print("data 1", form["id_user"])
#         return redirect(url_for("get_details", id_user=form["id_user"],
#                                 thoi_gian_dat=form["thoi_gian_dat"]))
#
#     extra_js = ["/static/js/main.js"]


class BaoCaoThangView(AdminBaseView):
    @expose('/')
    def bill(self):
        return self.render('/admin/BaoCaoThang.html')


class BaoCaoMatDoView(AdminBaseView):
    @expose('/')
    def bill(self):
        return self.render('/admin/BaoCaoMatDo.html')


class QuyDinhView(ReceptionistModelView):
    edit_modal = True
    can_edit = False
    can_create = False
    can_delete = False

    column_list = ['regulation', 'value']
    column_labels = {
        'regulation': 'Quy định',
        'value': 'Giá trị',
    }

    form_widget_args = {
        'regulation': {
            'readonly': False  # Allow editing of the primary key field
        }
    }

    column_formatters = {
        'regulation': lambda view, context, model, name: model.regulation.value,
    }

    # form_overrides = {
    #     'regulation': SelectField
    # }
    # form_args = {
    #     'regulation': {
    #         'label': 'Quy định',
    #         'choices': [(choice.name, choice.value) for choice in RegulationEnum],
    #         'coerce': lambda item: RegulationEnum[item] if item else None
    #     }
    # }

    def get_pk_value(self, model):
        return model.regulation.name


class QuyDinhViewAdmin(QuyDinhView):
    can_edit = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.quan_ly


def reviewer_choices():
    return LoaiPhong.query


class PhongView(AdminModelView):
    can_create = True
    can_view_details = True
    edit_modal = True
    details_modal = True

    column_list = ['id', 'loaiphong.loai_phong', 'tinh_trang']
    form_columns = ('id', 'id_loaiphong', 'tinh_trang')
    column_labels = {
        'id': "Phòng",
        'loaiphong.loai_phong': 'Loại phòng',
        'id_loaiphong': 'Loại phòng',
        'tinh_trang': 'Tình trạng',
    }

    form_widget_args = {
        'id': {
            'readonly': False  # Allow editing of the primary key field
        }
    }

    form_overrides = {
        'id_loaiphong': QuerySelectField
    }
    form_args = {
        'id_loaiphong': {
            'label': 'Loại Phòng',
            'query_factory': reviewer_choices,  # replace with your actual query factory function
            'allow_blank': False,
            'validators': [DataRequired()],
            'get_pk': lambda a: a.id,  # This is the field to use as the value (primary key)
            'get_label': 'loai_phong'
        }
    }


class LoaiPhongView(ReceptionistModelView):
    can_create = False
    can_view_details = True
    edit_modal = False
    details_modal = True
    can_edit = False
    can_delete = False

    column_searchable_list = ['loai_phong', 'mo_ta', 'dien_tich']
    column_filters = ['loai_phong', 'mo_ta', 'dien_tich']
    column_list = ['loai_phong', 'mo_ta', 'dien_tich']
    column_labels = {
        'loai_phong': "Loại phòng",
        'mo_ta': 'Mô tả',
        'dien_tich': 'Diện tích (m2)',
    }


class LoaiPhongViewAdmin(LoaiPhongView):
    can_create = True
    edit_modal = True
    can_edit = True
    can_delete = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.user_role == UserRole.quan_ly


admin.add_view(PhieuDatPhongView(PhieuDatThuePhong, db.session, name="Phiếu Đặt Phòng", endpoint="phieudatphong"))
admin.add_view(PhieuThuePhongView(PhieuDatThuePhong, db.session, name="Phiếu Thuê Phòng", endpoint="phieuthuephong"))
admin.add_view(BaoCaoThangView(name="Báo cáo tháng"))
admin.add_view(BaoCaoMatDoView(name="Báo cáo mật độ"))
# admin.add_view(QuyDinhView(QuyDinh, db.session, name="Quản lý quy định"))
admin.add_view(PhongView(Phong, db.session, name="Quản lý phòng"))
admin.add_view(LoaiPhongView(LoaiPhong, db.session, name="Loại phòng"))
admin.add_view(LoaiPhongViewAdmin(LoaiPhong, db.session, name="Loại phòng", endpoint="loaiphong_admin"))
admin.add_view(QuyDinhView(QuyDinh, db.session, name="Quy định"))
admin.add_view(QuyDinhViewAdmin(QuyDinh, db.session, name="Quy định", endpoint="quydinh_admin"))
admin.add_view(LogoutView(name="Đăng xuất"))
