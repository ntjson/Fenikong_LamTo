import io

import qrcode
import qrcode.image.svg


def bill_qr_svg(reference: str) -> str:
    image = qrcode.make(
        f"lamto-bill:{reference}",
        image_factory=qrcode.image.svg.SvgPathImage,
        box_size=10,
        border=2,
    )
    buffer = io.BytesIO()
    image.save(buffer)
    return buffer.getvalue().decode("utf-8")
