import qrcode #library that will generate and draw the image
from io import BytesIO #gives us a temporary memory where we construct the PNG image
from django.core.files import File

from .models import Registration

def generate_registration_qr_code(registration):


    qr = qrcode.make(str(registration.token))

    qr_buffer = BytesIO()

    qr.save(qr_buffer, format="PNG")

    # move the buffer bac to the beginning so django reads it
    qr_buffer.seek(0)

    #svae the generated QR code into registration.qr_code

    registration.qr_code.save(f"{registration.token}.png", File(qr_buffer), save=True)

    qr_buffer.close()#close the buffer after saving the image