# qrgen - QR Code Generator Django Project

## Overview

qrgen is a simple, mobile-friendly QR Code Generator web app built with Python and Django. It supports generating QR codes for plain text, URLs, phone numbers, emails, Wi-Fi login information, and image uploads with automatic QR code generation linking to uploaded images.

The UI is built with Django Templates, Bootstrap 5, and custom CSS for mobile-first responsive design. It includes optional features like session history of generated QR codes, dark/light theme toggle, share button, and an API endpoint for programmatic QR code generation.

## Features

- QR code generation for multiple input types
- Image upload and QR code linking to uploaded images
- Large preview and download button for QR codes
- Mobile-first UI with Bootstrap 5
- Dark/light mode toggle
- Session history of generated QR codes
- Share QR code button (on supported devices)
- API endpoint for QR generation
- Ready for deployment with whitenoise static file handling

## Installation

1. Clone or download the repository
2. Create and activate a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

*Note: You may need to create a requirements.txt file with needed packages: Django, qrcode, whitenoise*

## Running Locally

1. Apply migrations:

```bash
python manage.py migrate
```

2. Run the development server:

```bash
python manage.py runserver
```

3. Open your browser and navigate to `http://127.0.0.1:8000/`

## Static Files Collection (Production)

Before deploying, collect static files with:

```bash
python manage.py collectstatic
```

## Media Files

- Uploaded images are stored in `/media/uploads/`
- Generated QR codes are stored in `/media/qr/`
- Ensure your production server serves media files from the `/media/` URL path correctly.

## Deployment Notes

- Set `DEBUG = False` and configure `ALLOWED_HOSTS` in `qrgen/settings.py`
- Use whitenoise for static files in production (already integrated)
- Follow best practices for your hosting provider (PythonAnywhere, Railway, Render, etc.)

## Optional

- To use the API endpoint, POST JSON to `/api/generate/` with `type` and `data`.

## Contact

For any questions or issues, feel free to open an issue or contact the maintainer.
