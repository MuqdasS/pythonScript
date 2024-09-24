
import fitz  
import os

def extract_text_with_coords(page):
    """
    Extracts text blocks and their coordinates from a PDF page.
    """
    text_instances = []
    blocks = page.get_text("blocks")  # Extract text blocks
    print(f"Extracted {len(blocks)} blocks on page {page.number}")  # Print number of text blocks
    
    for block in blocks:
        block_text, block_rect = block[4], block[:4]  # Text and rectangle
        if block_text.strip():  # If text is not empty
            text_instances.append((block_text, block_rect))
            print(f"Text: {block_text.strip()}, Coords: {block_rect}")  # Print each block's text and coordinates
    return text_instances

def find_section_ranges(pdf_document, start_texts, end_texts):
    """
    Finds the start and end pages for each section defined by pairs of start and end texts.
    """
    total_pages = len(pdf_document)
    ranges = []
    
    for start_text, end_text in zip(start_texts, end_texts):
        start_page = None
        end_page = None
        
        for page_number in range(total_pages):
            page = pdf_document.load_page(page_number)
            text_blocks = extract_text_with_coords(page)
            
            for text, _ in text_blocks:
                if start_text in text:
                    if start_page is None:
                        start_page = page_number
                        print(f"Found start text '{start_text}' on page {start_page}")
                if end_text in text:
                    end_page = page_number
                    print(f"Found end text '{end_text}' on page {end_page}")
                    break  # Break out of loop once end_text is found
        
            if end_page is not None and start_page is not None:
                break  # Stop searching if both start and end texts are found
        
        if start_page is not None and end_page is not None and start_page <= end_page:
            ranges.append((start_text, end_text, start_page, end_page))
        else:
            print(f"Could not find valid range for start '{start_text}' and end '{end_text}'")

    return ranges

def crop_page(page, start_text, end_text):
    """
    Crops a page from the start_text to end_text.
    """
    text_instances = extract_text_with_coords(page)
    crop_boxes = []
    cropping = False
    
    for text, rect in text_instances:
        if start_text in text:
            cropping = True
            crop_boxes.append(rect)
        if cropping:
            crop_boxes.append(rect)
        if end_text in text:
            cropping = False
            crop_boxes.append(rect)
            break
    
    if not crop_boxes:
        return None  # Return None if no crop boxes were found
    
    # Calculate the cropping rectangle
    min_x = min([box[0] for box in crop_boxes])
    min_y = min([box[1] for box in crop_boxes])
    max_x = max([box[2] for box in crop_boxes])
    max_y = max([box[3] for box in crop_boxes])
    
    # Crop the image and return it
    pix = page.get_pixmap(clip=fitz.Rect(min_x, min_y, max_x, max_y))
    return pix

def save_cropped_section(pdf_document, part_number, start_page, end_page, output_folder, start_text, end_text):
    """
    Saves a cropped section of the PDF to a new file with part number.
    """
    output_pdf = fitz.open()
    for page_number in range(start_page, end_page + 1):
        page = pdf_document.load_page(page_number)
        cropped_pixmap = crop_page(page, start_text, end_text)
        if cropped_pixmap:
            temp_file = f"temp_page_{page_number}.png"
            cropped_pixmap.save(temp_file)
            new_page = output_pdf.new_page(width=cropped_pixmap.width, height=cropped_pixmap.height)
            new_page.insert_image(new_page.rect, filename=temp_file)
            os.remove(temp_file)  # Remove the temporary image file
    
    if len(output_pdf) > 0:
        section_filename = f"Part_{part_number}.pdf"
        section_path = os.path.join(output_folder, section_filename)
        output_pdf.save(section_path)
        output_pdf.close()
        print(f"Section saved: {section_filename}")
    else:
        print(f"Warning: Section 'Part_{part_number}' has no pages to save.")

def split_pdf_by_section_ranges(pdf_path, output_folder, start_texts, end_texts):
    """
    Splits the PDF into sections based on multiple start and end texts and crops the pages.
    """
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Find pages for each start and end section
    ranges = find_section_ranges(pdf_document, start_texts, end_texts)
    
    part_number = 1
    for start_text, end_text, start_page, end_page in ranges:
        # Save the cropped section with part number
        save_cropped_section(pdf_document, part_number, start_page, end_page, output_folder, start_text, end_text)
        part_number += 1

    pdf_document.close()

# Usage
pdf_path = 'ocr.pdf'
output_folder = 'path/folder'

# Define start and end texts for all sections of Schedule K-3
start_texts = [
    "Partner’s Share of Income, Deductions, Credits, etc.—International",
    "Partner’s Share of Partnership’s Other Current Year International Information",
    "Foreign Tax Credit Limitation",
    "Other Information for Preparation of Form 1116 or 1118",
    "Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDII)",
    "Distributions From Foreign Corporations to Partnership",
    "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",
    "Information Regarding Passive Foreign Investment Companies (PFICs)",
    "Partner’s Interest in Foreign Corporation Income (Section 960)",
    "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
    "Foreign Partner’s Character and Source of Income and Deductions",
    "Section 871(m) Covered Partnerships",
    "Reserved for Future Use",
    "Foreign Partner’s Distributive Share of Deemed Sale Items on Transfer of Partnership Interest"
]

end_texts = [
    "Partner’s Share of Partnership’s Other Current Year International Information",
    "Foreign Tax Credit Limitation",
    "Other Information for Preparation of Form 1116 or 1118",
    "Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDII)",
    "Distributions From Foreign Corporations to Partnership",
    "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",
    "Information Regarding Passive Foreign Investment Companies (PFICs)",
    "Partner’s Interest in Foreign Corporation Income (Section 960)",
    "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
    "Foreign Partner’s Character and Source of Income and Deductions",
    "Section 871(m) Covered Partnerships",
    "Reserved for Future Use",
    "Foreign Partner’s Distributive Share of Deemed Sale Items on Transfer of Partnership Interest",
    "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets ."
    
]

split_pdf_by_section_ranges(pdf_path, output_folder, start_texts, end_texts)
