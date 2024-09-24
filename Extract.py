import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import os
from difflib import SequenceMatcher

# Set paths to Tesseract and Poppler (required for OCR and PDF manipulation)
poppler_path = r"C:\Program Files\Release-24.07.0-0\poppler-24.07.0\Library\bin"  # Path to Poppler
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Path to Tesseract

def convert_scanned_to_text_pdf(scanned_pdf_path, ocr_pdf_path):
    """
    Convert a scanned PDF to a text-based PDF using OCR and print the OCR text output.
    """
    scanned_doc = fitz.open(scanned_pdf_path)
    ocr_doc = fitz.open()  # Create a new blank PDF

    for page_number in range(len(scanned_doc)):
        page = scanned_doc.load_page(page_number)
        pix = page.get_pixmap(dpi=300)  # High DPI for better OCR results
        image = Image.open(io.BytesIO(pix.tobytes()))

        # Perform OCR to extract the text-based version of the page
        ocr_result = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
        ocr_text = pytesseract.image_to_string(image)  # Extract text as string for debugging
        # print(f"OCR text from page {page_number}:\n{ocr_text}\n")  # Print the OCR text for debugging

        # Create a new PDF page from OCR result
        ocr_page = fitz.open("pdf", ocr_result)
        ocr_doc.insert_pdf(ocr_page)  # Insert OCR page into the new PDF

    ocr_doc.save(ocr_pdf_path)
    ocr_doc.close()
    scanned_doc.close()
    print(f"OCR PDF saved as: {ocr_pdf_path}")

def extract_text_blocks(pdf_path, output_text_path):
    """
    Extract all text blocks from the OCR PDF and save them to a text file for inspection.
    """
    doc = fitz.open(pdf_path)
    print("\nExtracting text blocks from the OCR PDF...")

    with open(output_text_path, 'w', encoding='utf-8') as text_file:
        for page_number in range(len(doc)):
            page = doc.load_page(page_number)
            blocks = page.get_text("blocks")  # Extract text blocks
            
            text_file.write(f"\n--- Page {page_number + 1} ---\n")
            for block in blocks:
                text = block[4]  # The text content of the block
                text_file.write(text.strip() + "\n")  # Write the text block content to file

    doc.close()
    print(f"Extracted text saved to: {output_text_path}")

def fuzzy_match(text, pattern, threshold=0.6):
    """
    Perform fuzzy matching between the text and pattern, returning True if similarity is above threshold.
    """
    similarity = SequenceMatcher(None, text, pattern).ratio()
    return similarity >= threshold

def find_text_coordinates(pdf_path, start_text, end_text):
    """
    Finds the coordinates of start and end text within the text-based PDF using fuzzy matching.
    """
    doc = fitz.open(pdf_path)
    coordinates = []

    for page_number in range(len(doc)):
        page = doc.load_page(page_number)
        blocks = page.get_text("blocks")  # Extract text blocks

        start_coords = None
        end_coords = None

        for block in blocks:
            text, rect = block[4], block[:4]
            if fuzzy_match(text, start_text) and start_coords is None:
                start_coords = (rect[0], rect[1], rect[2], rect[3])  # Left, Top, Right, Bottom
                print(f"Found start text '{start_text}' on page {page_number} at {start_coords}")

            if fuzzy_match(text, end_text) and start_coords is not None:
                end_coords = (rect[0], rect[1], rect[2], rect[3])
                print(f"Found end text '{end_text}' on page {page_number} at {end_coords}")
                coordinates.append((page_number, start_coords, end_coords))
                break  # Stop searching after finding end text

        if start_coords and not end_coords:
            print(f"End text '{end_text}' not found after start text on page {page_number}.")

    doc.close()
    if not coordinates:
        print("No coordinates found. Check if start and end text are correct.")
    return coordinates

def crop_sections_from_original_pdf(original_pdf_path, sections, output_folder):
    """
    Crops sections from the original scanned PDF using coordinates from the OCR PDF and saves them as separate PDFs.
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    doc = fitz.open(original_pdf_path)

    for idx, (page_num, start_coords, end_coords) in enumerate(sections):
        page = doc.load_page(page_num)

        # Print the sections to debug
        print(f"Section {idx + 1} on page {page_num}: Start Coords: {start_coords}, End Coords: {end_coords}")

        try:
            # Unpack the coordinates
            left_start, top_start, right_start, bottom_start = start_coords
            left_end, top_end, right_end, bottom_end = end_coords

            # Define a rectangle that spans from the start to the end text coordinates
            left = min(left_start, left_end)
            top = min(top_start, top_end)
            right = max(right_start, right_end)
            bottom = max(bottom_start, bottom_end)
            rect = fitz.Rect(left, top, right, bottom)

            # Check if the cropping rectangle is within the page dimensions
            page_rect = page.rect
            if rect.x0 < page_rect.x0 or rect.y0 < page_rect.y0 or rect.x1 > page_rect.x1 or rect.y1 > page_rect.y1:
                print(f"Adjusted cropping rectangle to fit within page {page_num}: {rect}")
                rect.intersect(page_rect)  # Adjust the rectangle to fit within the page bounds

            # Ensure the width and height of the cropping rectangle are positive
            if rect.width <= 0 or rect.height <= 0:
                print(f"Invalid cropping dimensions on page {page_num}: {rect}")
                continue

            # Debug: Print the cropping rectangle coordinates
            print(f"Cropping rectangle on page {page_num}: {rect}")

            # Create a new document and a new page
            cropped_doc = fitz.open()  # Create a new empty PDF
            cropped_page = cropped_doc.new_page(width=rect.width, height=rect.height)

            # Insert the cropped content into the new PDF page
            cropped_page.show_pdf_page(fitz.Rect(0, 0, rect.width, rect.height), doc, page_num, clip=rect)

            # Save the cropped section as a PDF
            output_path = os.path.join(output_folder, f"Cropped_Section_{idx + 1}.pdf")
            cropped_doc.save(output_path)
            cropped_doc.close()

            print(f"Saved cropped section as PDF: {output_path}")

        except Exception as crop_error:
            print(f"Error cropping section from page {page_num}: {crop_error}")

    doc.close()

# File paths (make sure to specify correct paths)
scanned_pdf_path = "Client2.pdf"  # Path to the original scanned PDF
ocr_pdf_path = "ocr3.pdf"  # Specify a valid path for the OCR PDF
output_text_path = "ocr_output2.txt"  # Path to save the extracted OCR text
output_folder = "output"  # Folder where cropped sections will be saved

# Define start and end text
start_text = "Partner’s Share of Partnership’s Other Current Year International Information"  # Example start text
end_text = "Foreign Tax Credit Limitation"  # Example end text

try:
    # Step 1: Convert scanned PDF to text-based PDF using OCR
    convert_scanned_to_text_pdf(scanned_pdf_path, ocr_pdf_path)

    # Step 2: Extract text blocks from the OCR PDF and save to file
    extract_text_blocks(ocr_pdf_path, output_text_path)

    # Step 3: Find coordinates of start and end text in the OCR PDF
    sections = find_text_coordinates(ocr_pdf_path, start_text, end_text)

    # Step 4: Crop sections from the original scanned PDF using the found coordinates
    if sections:
        crop_sections_from_original_pdf(scanned_pdf_path, sections, output_folder)
    else:
        print("No sections found to crop. Check the start and end text accuracy.")

except Exception as e:
    print(f"An error occurred: {e}")



