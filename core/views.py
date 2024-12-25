import pytesseract
import cv2
import re
from django.shortcuts import render
from django.core.files.storage import FileSystemStorage
from django.conf import settings
import os

# Add at the top of your file if using Windows
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

def home(request):
    return render(request, 'core/home.html')

def extract_phone_numbers(image_path):
    try:
        # Read image using OpenCV
        image = cv2.imread(image_path)
        
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding to preprocess the image
        threshold = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Perform OCR
        text = pytesseract.image_to_string(threshold)
        
        # Enhanced pattern for WhatsApp numbers
        patterns = [
            r'\+\d{1,3}\s*\(\d{3}\)\s*\d{3}[-\s]?\d{4}',  # +1 (437) 873-6750
            r'\+\d{1,3}\s*\d{5}\s*\d{5}',                  # +91 73562 45752
            r'\+\d{1,3}\s*\d{10}',                         # +91 7356245752
            r'\+\d{1,3}\s*\d{2}\s*\d{3}\s*\d{4}'          # +971 56 126 3787
        ]
        
        # Combine patterns
        combined_pattern = '|'.join(patterns)
        
        # Find all matches
        phone_numbers = re.findall(combined_pattern, text)
        
        # Clean the numbers (remove spaces and hyphens)
        cleaned_numbers = [re.sub(r'[-\s()]', '', number) for number in phone_numbers]
        
        # Remove duplicates while preserving order
        unique_numbers = list(dict.fromkeys(cleaned_numbers))
        
        return unique_numbers
        
    except Exception as e:
        print(f"Error occurred: {str(e)}")
        return []

def upload_screenshot(request):
    if request.method == 'POST' and request.FILES.get('whatsapp_image'):
        image = request.FILES['whatsapp_image']
        
        # Check file type
        allowed_types = ['image/jpeg', 'image/png', 'image/jpg']
        if image.content_type not in allowed_types:
            return render(request, 'core/upload.html', {
                'error': 'Please upload only JPEG or PNG images.'
            })
            
        # Check file size
        if image.size > 5 * 1024 * 1024:
            return render(request, 'core/upload.html', {
                'error': 'File size should be less than 5MB.'
            })

        try:
            # Delete existing images
            screenshots_dir = os.path.join(settings.MEDIA_ROOT, 'whatsapp_screenshots')
            if os.path.exists(screenshots_dir):
                for filename in os.listdir(screenshots_dir):
                    file_path = os.path.join(screenshots_dir, filename)
                    try:
                        if os.path.isfile(file_path):
                            os.unlink(file_path)
                    except Exception as e:
                        print(e)

            # Create directory if it doesn't exist
            os.makedirs(screenshots_dir, exist_ok=True)

            fs = FileSystemStorage()
            filename = 'whatsapp-image.' + image.name.split('.')[-1]
            saved_path = fs.save(f'whatsapp_screenshots/{filename}', image)
            
            # Get full path of saved image
            full_path = os.path.join(settings.MEDIA_ROOT, saved_path)
            
            # Extract phone numbers
            phone_numbers = extract_phone_numbers(full_path)
            
            if phone_numbers:
                return render(request, 'core/results.html', {
                    'phone_numbers': phone_numbers,
                    'count': len(phone_numbers)
                })
            else:
                return render(request, 'core/upload.html', {
                    'error': 'No phone numbers found in the image.'
                })

        except Exception as e:
            return render(request, 'core/upload.html', {
                'error': f'An error occurred: {str(e)}'
            })

    return render(request, 'core/upload.html')