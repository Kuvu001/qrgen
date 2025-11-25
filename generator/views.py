import os
import qrcode
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from django.http import HttpResponse, JsonResponse, FileResponse, Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from urllib.parse import quote as urlquote
from django.urls import reverse
from django.views.decorators.http import require_http_methods

def index(request):
    """Render the main QR generator page with session history and theme preference."""
    qr_history = request.session.get('qr_history', [])
    theme = request.session.get('theme', 'light')
    return render(request, 'generator/index.html', {
        'qr_history': qr_history,
        'theme': theme,
    })

@require_http_methods(["POST"])
def generate_qr(request):
    """Generate QR code based on POSTed form data for various QR types."""
    qr_type = request.POST.get('qr_type', 'text')
    data = None
    error = None

    # Handle based on QR type
    if qr_type == 'text':
        data = request.POST.get('text', '').strip()
    elif qr_type == 'link':
        data = request.POST.get('link', '').strip()
    elif qr_type == 'phone':
        phone = request.POST.get('phone', '').strip()
        data = f"tel:{phone}" if phone else None
    elif qr_type == 'email':
        email = request.POST.get('email', '').strip()
        data = f"mailto:{email}" if email else None
    elif qr_type == 'wifi':
        ssid = request.POST.get('wifi_ssid', '').strip()
        password = request.POST.get('wifi_password', '').strip()
        encryption = request.POST.get('wifi_encryption', 'WPA').strip()
        if ssid:
            # Format for WiFi QR code per standard:
            # WIFI:T:WPA;S:SSID;P:password;;
            data = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
        else:
            data = None
    elif qr_type == 'image':
        # Handle file upload and generate QR linking to uploaded image URL
        uploaded_file = request.FILES.get('upload_image')
        if uploaded_file:
            upload_path = os.path.join(settings.MEDIA_ROOT, 'uploads')
            os.makedirs(upload_path, exist_ok=True)
            save_path = os.path.join(upload_path, uploaded_file.name)
            with open(save_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            # Build absolute URL to uploaded image
            image_url = request.build_absolute_uri(settings.MEDIA_URL + 'uploads/' + uploaded_file.name)
            data = image_url
        else:
            data = None
    else:
        data = request.POST.get('text', '').strip()

    if not data:
        error = "No valid input data provided for QR code generation."
        return render(request, 'generator/index.html', {'error': error})

    # Generate QR code image with high resolution PNG
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    # Save to bytes buffer
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    image_png = buffer.getvalue()

    # Save QR image to media/qr/ folder
    qr_folder = os.path.join(settings.MEDIA_ROOT, 'qr')
    os.makedirs(qr_folder, exist_ok=True)
    qr_filename = f"qr_{request.session.session_key or 'anon'}.png"
    qr_path = os.path.join(qr_folder, qr_filename)
    with open(qr_path, 'wb') as f:
        f.write(image_png)

    # Save record in session history
    qr_history = request.session.get('qr_history', [])
    qr_url = settings.MEDIA_URL + 'qr/' + qr_filename
    qr_history.append({
        'type': qr_type,
        'data': data,
        'qr_url': qr_url,
        'filename': qr_filename,
    })
    # Keep only last 10 items
    request.session['qr_history'] = qr_history[-10:]
    request.session.modified = True

    theme = request.session.get('theme', 'light')

    return render(request, 'generator/index.html', {
        'qr_url': qr_url,
        'qr_filename': qr_filename,
        'qr_type': qr_type,
        'data': data,
        'qr_history': qr_history[-10:],
        'theme': theme,
    })

def download_qr(request, qr_filename):
    """Serve the QR code PNG file for download."""
    qr_path = os.path.join(settings.MEDIA_ROOT, 'qr', qr_filename)
    if not os.path.exists(qr_path):
        raise Http404("QR code image does not exist.")
    response = FileResponse(open(qr_path, 'rb'), content_type="image/png")
    response['Content-Disposition'] = f'attachment; filename="{urlquote(qr_filename)}"'
    return response

@csrf_exempt
@require_http_methods(["POST"])
def api_generate_qr(request):
    """
    API endpoint to generate QR code programmatically.
    Expects JSON body with keys:
    - 'type': QR code type (text, link, phone, email, wifi, image)
    - 'data': string data for QR code
    Returns JSON with 'qr_url' to generated QR PNG or error message.
    """
    import json
    try:
        body = json.loads(request.body)
        qr_type = body.get('type', 'text')
        data = body.get('data', '').strip()

        if not data:
            return JsonResponse({'error': 'No data provided.'}, status=400)

        # If qr_type is wifi, expect data is dict with ssid, password, encryption keys, else data remains string
        if qr_type == 'wifi':
            ssid = data.get('ssid')
            password = data.get('password')
            encryption = data.get('encryption', 'WPA')
            if not ssid:
                return JsonResponse({'error': 'SSID is required for WiFi QR code.'}, status=400)
            data_str = f"WIFI:T:{encryption};S:{ssid};P:{password};;"
        else:
            data_str = data

        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data_str)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR as PNG bytes
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        image_png = buffer.getvalue()

        # Save file
        qr_folder = os.path.join(settings.MEDIA_ROOT, 'qr')
        os.makedirs(qr_folder, exist_ok=True)
        qr_filename = f"api_qr_{request.session.session_key or 'anon'}.png"
        qr_path = os.path.join(qr_folder, qr_filename)
        with open(qr_path, 'wb') as f:
            f.write(image_png)

        qr_url = request.build_absolute_uri(settings.MEDIA_URL + 'qr/' + qr_filename)

        return JsonResponse({'qr_url': qr_url})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

def toggle_theme(request):
    """Toggle dark/light theme preference in session."""
    current_theme = request.session.get('theme', 'light')
    new_theme = 'dark' if current_theme == 'light' else 'light'
    request.session['theme'] = new_theme
    return JsonResponse({'theme': new_theme})
