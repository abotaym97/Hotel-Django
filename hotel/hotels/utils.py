from django.core.mail import EmailMultiAlternatives
from django.conf import settings

# هذا الوظيفة ترسل إيميل تأكيد الحجز للضيف بعد أن يتم تأكيد الحجز بنجاح
def send_booking_confirmation_email(booking):

    
    




    
    # لا ترسل الإيميل أكثر من مرة
    if booking.confirmation_email_sent:
        return

    # إذا لا يوجد إيميل للضيف
    if not booking.guest_email:
        return

    subject = f"Booking Confirmation - {booking.booking_code}"

    # نسخة نصية احتياطية
    text_content = f"""
Dear {booking.guest_name},

Thank you for choosing NajafDo Hotel.

Your reservation has been confirmed successfully.

Booking Details
----------------
Booking Code: {booking.booking_code}

Room Type: {booking.room.room_type.name}

Check-in: {booking.check_in}
Check-out: {booking.check_out}

Adults: {booking.adults}
Children: {booking.children}

Total Price: {booking.total_price}

Payment Status: {booking.payment_status}
Payment Method: {booking.payment_method}

We look forward to welcoming you.

Best regards,
NajafDo Hotel
"""



    # HTML Email
    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Booking Confirmation</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    font-family: Arial, Helvetica, sans-serif;
">

    <div style="
        max-width: 650px;
        margin: 40px auto;
        background-color: #ffffff;
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 20px rgba(0,0,0,0.08);
    ">

        <!-- Header -->
        <div style="
            background-color: #111111;
            padding: 30px;
            text-align: center;
        ">
            <h1 style="
                margin: 0;
                color: #ffffff;
                font-size: 28px;
                letter-spacing: 1px;
            ">
                NajafDo Hotel
            </h1>

            <p style="
                margin: 8px 0 0;
                color: #d4af37;
                font-size: 14px;
            ">
                BOOKING CONFIRMATION
            </p>
        </div>

        <!-- Content -->
        <div style="padding: 35px;">

            <h2 style="
                margin-top: 0;
                color: #222222;
                font-size: 24px;
            ">
                Booking Confirmed
            </h2>

            <p style="
                color: #555555;
                font-size: 15px;
                line-height: 1.7;
            ">
                Dear <strong>{booking.guest_name}</strong>,
            </p>

            <p style="
                color: #555555;
                font-size: 15px;
                line-height: 1.7;
            ">
                Thank you for choosing NajafDo Hotel.
                Your reservation has been successfully confirmed.
            </p>

            <!-- Booking Code -->
            <div style="
                margin: 25px 0;
                padding: 18px;
                background-color: #f8f8f8;
                border-radius: 8px;
                text-align: center;
            ">

                <p style="
                    margin: 0 0 6px;
                    color: #777777;
                    font-size: 12px;
                    text-transform: uppercase;
                ">
                    Booking Code
                </p>

                <strong style="
                    color: #111111;
                    font-size: 22px;
                    letter-spacing: 1px;
                ">
                    {booking.booking_code}
                </strong>

            </div>

            <!-- Booking Details -->
            <h3 style="
                color: #222222;
                font-size: 18px;
                margin-bottom: 15px;
            ">
                Reservation Details
            </h3>

            <table style="
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
            ">

                

                <tr>
                    <td style="padding: 10px 0; color: #777777;">
                        Room Type
                    </td>
                    <td style="
                        padding: 10px 0;
                        text-align: right;
                        color: #222222;
                    ">
                        {booking.room.room_type.name}
                    </td>
                </tr>

                <tr>
                    <td style="padding: 10px 0; color: #777777;">
                        Check-in
                    </td>
                    <td style="
                        padding: 10px 0;
                        text-align: right;
                        color: #222222;
                    ">
                        {booking.check_in}
                    </td>
                </tr>

                <tr>
                    <td style="padding: 10px 0; color: #777777;">
                        Check-out
                    </td>
                    <td style="
                        padding: 10px 0;
                        text-align: right;
                        color: #222222;
                    ">
                        {booking.check_out}
                    </td>
                </tr>

                <tr>
                    <td style="padding:8px 0; color:#777;">Nights</td>
                    <td style="padding:8px 0; text-align:right;">
                        <strong>{booking.nights}</strong>
                    </td>
                </tr>

                <tr>
                    <td style="padding: 10px 0; color: #777777;">
                        Guests
                    </td>
                    <td style="
                        padding: 10px 0;
                        text-align: right;
                        color: #222222;
                    ">
                        {booking.adults} Adults,
                        {booking.children} Children
                    </td>
                </tr>

            </table>

            <!-- Payment -->
            <div style="
                margin-top: 25px;
                padding: 20px;
                background-color: #f7faf7;
                border-radius: 8px;
            ">

                <h3 style="
                    margin-top: 0;
                    color: #222222;
                    font-size: 17px;
                ">
                    Payment
                </h3>

                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Payment Status:
                    <strong style="color: #16803c;">
                        {booking.payment_status}
                    </strong>
                </p>

                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Payment Method:
                    <strong>
                        {booking.payment_method}
                    </strong>
                </p>



                <!-- Price Details -->
                <h3 style="
                    margin: 20px 0 10px;
                    color: #222222;
                    font-size: 17px;
                ">
                    Price Details
                </h3>

                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Room Price:
                    <strong>
                        {booking.room.room_type.price} IQD × {booking.nights} night(s)
                    </strong>
                </p>

                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Room Total:
                    <strong>
                        {booking.room.room_type.price * booking.nights} IQD
                    </strong>
                </p>

                {f'''
                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Meal:
                    <strong>
                        {booking.meal_option.name}
                    </strong>
                </p>

                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Meal Price:
                    <strong>
                        {booking.meal_price} IQD × {booking.nights} night(s)
                    </strong>
                </p>

                <p style="
                    margin: 8px 0;
                    color: #555555;
                ">
                    Meal Total:
                    <strong>
                        {booking.meal_price * booking.nights} IQD
                    </strong>
                </p>
                ''' if booking.meal_option else ''}

                <p style="
                    margin: 15px 0;
                    color: #222222;
                    font-size: 18px;
                ">
                    Total:
                    <strong>
                        {booking.total_price} IQD
                    </strong>
                </p>

            </div>

            <div style="margin-top: 30px;">

            <h3 style="
                font-size: 18px;
                color: #222222;
                margin-bottom: 15px;
            ">
                General conditions:
            </h3>

            <ul style="
                padding-left: 25px;
                color: #333333;
                font-size: 15px;
                line-height: 1.7;
            ">

                <li>
                    Check-in time is 15:00. Early Check-in (before 15:00 and not earlier than 06:00)
                    is subject to availability. Check-in earlier than 06:00 is charged as a full room night.
                </li>

                <li>
                    Check-out time is 12:00. Late Check-out (after 12:00 and not later than 14:00)
                    is subject to availability. Check-out till 18:00 is charged at 50% of the daily room rate.
                    Check-out after 18:00 is charged as a full room night.
                </li>

                <li>
                    Cancellation policy: Any cancellation—regardless of notice period—will incur
                    a one-night charge as a cancellation fee.
                </li>

                <li>
                    In case of a “No Show”, the first night will be charged.
                </li>

                <li>
                    Please notify us of any schedule changes by calling or emailing us.
                </li>

            </ul>

        </div>

            <p style="
                margin-top: 30px;
                color: #555555;
                font-size: 15px;
                line-height: 1.7;
            ">
                We look forward to welcoming you to NajafDo Hotel.
            </p>

        </div>

        <!-- Footer -->
        <div style="
            background-color: #f8f8f8;
            padding: 25px;
            text-align: center;
        ">

            <p style="
                margin: 0;
                color: #555555;
                font-size: 13px;
            ">
                NajafDo Hotel
            </p>

            <p style="
                margin: 8px 0 0;
                color: #555555;
                font-size: 12px;
            ">
                Maydan Square - Old City - Najaf - Iraq
            </p>

            <p style="
                margin: 8px 0 0;
                color: #555555;
                font-size: 12px;
            ">
                <a href="https://najafdo.com" style="color: #555555; text-decoration: none;">
                    https://najafdo.com
                </a>
                &nbsp; | &nbsp;
                Tel: +9647821338040
            </p>

            <p style="
                margin: 8px 0 0;
                color: #555555;
                font-size: 12px;
            ">
                Email:
                <a href="mailto:reservation@najafdo.com" style="color: #555555; text-decoration: none;">
                    reservation@najafdo.com
                </a>
            </p>

            <p style="
                margin: 12px 0 0;
                color: #888888;
                font-size: 12px;
            ">
                Thank you for choosing us.
            </p>

        </div>

    </div>

</body>
</html>
"""

    # إنشاء الإيميل
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[booking.guest_email],
    )

    # إضافة نسخة HTML
    email.attach_alternative(html_content, "text/html")

    # إرسال
    email.send(fail_silently=False)

    # تسجيل أن إيميل التأكيد تم إرساله
    booking.confirmation_email_sent = True
    booking.save(update_fields=["confirmation_email_sent"])














#دالة لإرسال إشعار للحجز الجديد إلى قسم الاستقبال
def send_reception_booking_notification(booking):

    nights = (booking.check_out - booking.check_in).days

    if booking.reception_email_sent:
        return

    subject = f"New Booking - {booking.booking_code}"

    text_content = f"""
New Booking Confirmed

Booking Code: {booking.booking_code}

Guest Information
-----------------
Name: {booking.guest_name}
Email: {booking.guest_email}
Phone: {booking.guest_phone}
Country: {booking.guest_country}

Booking Details
---------------
<p>
    Booking Status:
    <strong>{booking.booking_status}</strong>
</p>

<p>
    Confirmed By:
    <strong>{booking.confirmed_by}</strong>
</p>
Room: {booking.room.room_number}
Room Type: {booking.room.room_type.name}

Check-in: {booking.check_in}
Check-out: {booking.check_out}

Adults: {booking.adults}
Children: {booking.children}

Payment
-------
Payment Status: {booking.payment_status}
Payment Method: {booking.payment_method}

Total Price: {booking.total_price} IQD

Please check the reservation in the hotel booking system.
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>New Booking</title>
</head>

<body style="
    margin: 0;
    padding: 0;
    background-color: #f5f5f5;
    font-family: Arial, Helvetica, sans-serif;
">

<div style="
    max-width: 650px;
    margin: 40px auto;
    background: #ffffff;
    border-radius: 12px;
    overflow: hidden;
">

    <div style="
        background-color: #111111;
        padding: 28px;
        text-align: center;
    ">
        <h1 style="
            margin: 0;
            color: #ffffff;
            font-size: 26px;
        ">
            NajafDo Hotel
        </h1>

        <p style="
            margin: 8px 0 0;
            color: #d4af37;
            font-size: 14px;
        ">
            NEW BOOKING
        </p>
    </div>

    <div style="padding: 30px;">

        <h2 style="
            margin-top: 0;
            color: #222222;
        ">
            New Booking Confirmed
        </h2>

        <div style="
            background: #f8f8f8;
            padding: 18px;
            border-radius: 8px;
            text-align: center;
            margin-bottom: 25px;
        ">
            <p style="
                margin: 0 0 6px;
                color: #777777;
                font-size: 12px;
            ">
                BOOKING CODE
            </p>

            <strong style="
                font-size: 22px;
                color: #111111;
            ">
                {booking.booking_code}
            </strong>
        </div>

        <h3>Guest Information</h3>

        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="padding:8px 0; color:#777;">Name</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.guest_name}
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Email</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.guest_email}
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Phone</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.guest_phone}
                </td>
            </tr>
        </table>

        <h3 style="margin-top:25px;">Booking Details</h3>

        <table style="width:100%; border-collapse:collapse;">
            <tr>
                <td style="padding:8px 0; color:#777;">Booking Status</td>
                <td style="padding:8px 0; text-align:right;">
                    <strong>{booking.booking_status}</strong>
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Confirmed By</td>
                <td style="padding:8px 0; text-align:right;">
                    <strong>{booking.confirmed_by}</strong>
                </td>
            </tr>
            <tr>
                <td style="padding:8px 0; color:#777;">Room</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.room.room_number}
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Room Type</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.room.room_type.name}
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Check-in</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.check_in}
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Check-out</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.check_out}
                </td>
            </tr>

            <tr>
                <td style="padding:8px 0; color:#777;">Nights</td>
                <td style="padding:8px 0; text-align:right;">
                    <strong>{nights}</strong>
                </td>
            </tr>


            <tr>
                <td style="padding:8px 0; color:#777;">Guests</td>
                <td style="padding:8px 0; text-align:right;">
                    {booking.adults} Adults,
                    {booking.children} Children
                </td>
            </tr>
        </table>

        <div style="
            margin-top:25px;
            padding:20px;
            background:#f7faf7;
            border-radius:8px;
        ">

            <h3 style="margin-top:0;">Payment</h3>

            <p>
                Payment Status:
                <strong>{booking.payment_status}</strong>
            </p>

            <p>
                Payment Method:
                <strong>{booking.payment_method}</strong>
            </p>

            <p style="font-size:18px;">
                Total:
                <strong>{booking.total_price}</strong>
            </p>

        </div>

        <p style="
            margin-top:30px;
            color:#555;
        ">
            Please check the reservation in the hotel booking system.
        </p>

    </div>

</div>

</body>
</html>
"""

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[settings.RECEPTION_EMAIL],
    )

    email.attach_alternative(html_content, "text/html")

    email.send(fail_silently=False)

    booking.reception_email_sent = True
    booking.save(update_fields=["reception_email_sent"])