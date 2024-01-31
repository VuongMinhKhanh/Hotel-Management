import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

# thiết lập port và server name

smtp_port = 587  # Standard secure SMTP port
smtp_server = "smtp.gmail.com"  # Google SMTP Server

# địa chỉ email của mình
email_from = "howtocarrythisteam@gmail.com"
alias_email = "receptionist@hotelier.com"
sender_name = "Hotelier"
# một danh sách các địa chỉ mail cần gửi file.
# email_list = ["2151050191khanh@ou.edu.vn"]

# Mật khẩu ứng dụng/ app password là từ khóa tìm kiếm trong mục quản lý gmail . tạo một app sẽ có mật khẩu này, tương  ứng với  email. một gmail có thể tạo nhiều app.
pswd = "cayh sawm rums qtue"


def send_files(email_list, path):
    attachment = open(path, 'rb')  # r for read and b for binary
    filename = os.path.abspath(path)
    for person in email_list:
        subject = "GỬI HÓA ĐƠN PHÒNG"
        body = f"Xin chào anh/chị, chúng tôi xin gửi hóa đơn của phòng"
        msg = MIMEMultipart()
        msg['From'] = f"{sender_name} <{alias_email}>"
        msg['To'] = person
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        # Định nghĩa một file để gửi
        # filename = 'blogs/The Lifelong Learning Advantage - Unlocking Your Full Potential.txt'

        print(attachment)
        # Encode as base 64
        attachment_package = MIMEBase('application', 'octet-stream')
        attachment_package.set_payload((attachment).read())
        encoders.encode_base64(attachment_package)

        # Encode the filename to handle non-ASCII characters
        basename = os.path.basename(filename)
        try:
            # Header class handles encoding of non-ASCII characters
            from email.header import Header
            attachment_package.add_header('Content-Disposition', 'attachment',
                                          filename=(Header(basename, 'utf-8').encode()))
        except Exception as e:
            # Fallback to a filename that does not contain special characters
            safe_basename = basename.encode('utf-8').decode('ascii', 'ignore')
            attachment_package.add_header('Content-Disposition', 'attachment', filename=safe_basename)
        msg.attach(attachment_package)

        # Cast as string
        text = msg.as_string()

        # Connect with the server
        print("Connecting to server...")
        TIE_server = smtplib.SMTP(smtp_server, smtp_port)
        TIE_server.starttls()
        TIE_server.login(email_from, pswd)
        print("Succesfully connected to server")
        print()

        # Send emails to "person" as list is iterated
        print(f"Sending email to: {person}...")
        TIE_server.sendmail(email_from, person, text)
        print(f"Email sent to: {person}")

    # Close the port
    TIE_server.quit()
    # Delete file
    attachment.close()
    # print("Path", path)
    os.remove(filename) # The process cannot access the file because it is being used by another process

# Run the function
# send_emails(email_list)


def compose_receipt_file(receipt):
    # print("receipt", receipt)
    form = '''<form method="post" id="receipt">
                <h2 class="text-center">HÓA ĐƠN THANH TOÁN</h2>
                <div class="mt-1 mb-1">
                    <div class="row g-3 d-flex align-items-center justify-content-center">
                        <div class="col-md-6">
                            <div class="form-floating">
                                <input id="room_type" class="form-control" type="text" style="background: white"
                                       value="{rooms}" disabled>
                                <label>Các phòng thuê</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating">
                                <input id="room_quantity" class="form-control" type="text" style="background: white"
                                       value="{full_name}" disabled>
                                <label class="" for="">Người đặt phòng</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating date" id="date3" data-target-input="nearest">
                                <input id="checkin" class="form-control" type="text" style="background: white"
                                       value="{checkin}" disabled>
                                <label for="checkin">Ngày nhận phòng</label>
                            </div>
                        </div>
                        <div class="col-md-6">
                            <div class="form-floating date" id="date4" data-target-input="nearest">
                                <input id="checkout" class="form-control" type="text" style="background: white"
                                       value="{checkout}" disabled>
                                <label for="checkout"> Ngày trả phòng</label>
                            </div>
                        </div>
                        <div class="col-md-2">
                            <div class="form-floating">
                                <h2>Tổng tiền</h2>
                            </div>
                        </div>
                        <div class="col-md-10">
                            <div class="">
                                <h2 id="room_type" class=" text-danger text-center bg-white "
                                    style="font-size: 3em">{str_price} VND</h2>
                            </div>
                        </div>
                    </div>
                </div>
            </form>'''.format(rooms=receipt["rooms"], full_name=receipt["booker_full_name"],
                               checkin=receipt["booking_time"][0]["thoi_gian_thue"], checkout=receipt["booking_time"][0]["thoi_gian_tra"],
                              str_price=receipt["str_price"])
    return form
