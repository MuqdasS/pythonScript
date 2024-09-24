import fitz  # PyMuPDF
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_with_coords(page):
    """
    Extracts text blocks and their coordinates from a PDF page.
    """
    text_instances = []
    blocks = page.get_text("blocks")
    print(f"Extracted {len(blocks)} blocks on page {page.number}")
    
    for block in blocks:
        block_text, block_rect = block[4], block[:4]
        if block_text.strip():
            text_instances.append((block_text, block_rect))
            print(f"Text: {block_text.strip()}, Coords: {block_rect}")
    return text_instances

def find_section_ranges(pdf_document, start_texts_with_multiple_ends):
    total_pages = len(pdf_document)
    ranges = []
    
    for start_texts, end_texts in start_texts_with_multiple_ends:
        start_page = None
        end_page = None
        
        for page_number in range(total_pages):
            page = pdf_document.load_page(page_number)
            text_blocks = extract_text_with_coords(page)

            for text, _ in text_blocks:
                if any(start_text in text for start_text in start_texts) and start_page is None:
                    start_page = page_number
                    print(f"Found start text on page {start_page}")
                if start_page is not None and any(end_text in text for end_text in end_texts):
                    end_page = page_number
                    print(f"Found end text on page {end_page} (matching one of: {end_texts})")
                    break

            if end_page is not None and start_page is not None:
                break

        if start_page is not None and end_page is not None and start_page <= end_page:
            ranges.append((start_texts, start_page, end_page))
        else:
            print(f"Could not find valid range for start '{start_texts}' and end texts {end_texts}")

    return ranges

def crop_page(page, start_texts, end_texts):
    """
    Crops a page from the first found start_text to the first found end_text.
    """
    text_instances = extract_text_with_coords(page)
    crop_boxes = []
    cropping = False
    
    for text, rect in text_instances:
        if any(start_text in text for start_text in start_texts):
            cropping = True
            crop_boxes.append(rect)
        if cropping:
            crop_boxes.append(rect)
        if any(end_text in text for end_text in end_texts):
            cropping = False
            crop_boxes.append(rect)
            break
    
    if not crop_boxes:
        return None  # Return None if no crop boxes were found
    
    min_x = min(box[0] for box in crop_boxes)
    min_y = min(box[1] for box in crop_boxes)
    max_x = max(box[2] for box in crop_boxes)
    max_y = max(box[3] for box in crop_boxes)
    
    pix = page.get_pixmap(clip=fitz.Rect(min_x, min_y, max_x, max_y))
    return pix

def save_cropped_section(pdf_document, part_number, start_page, end_page, output_folder, start_texts, end_texts):
    """
    Saves a cropped section of the PDF to a new file with part number.
    """
    output_pdf = fitz.open()
    for page_number in range(start_page, end_page + 1):
        page = pdf_document.load_page(page_number)
        cropped_pixmap = crop_page(page, start_texts, end_texts)
        if cropped_pixmap:
            new_page = output_pdf.new_page(width=cropped_pixmap.width, height=cropped_pixmap.height)
            new_page.insert_image(new_page.rect, pixmap=cropped_pixmap)
            cropped_pixmap = None  # Release memory immediately
    
    if len(output_pdf) > 0:
        section_filename = f"Part_{part_number}.pdf"
        section_path = os.path.join(output_folder, section_filename)
        output_pdf.save(section_path)
        output_pdf.close()
        print(f"Section saved: {section_filename}")
    else:
        print(f"Warning: Section 'Part_{part_number}' has no pages to save.")

def split_pdf_by_section_ranges(pdf_path, output_folder, start_texts_with_multiple_ends):
    # Ensure the output folder exists
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Open the PDF file
    pdf_document = fitz.open(pdf_path)
    
    # Find pages for each start and end section
    ranges = find_section_ranges(pdf_document, start_texts_with_multiple_ends)
    
    part_number = 0
    for start_texts, start_page, end_page in ranges:
        end_texts = start_texts_with_multiple_ends[part_number][1]  # Get corresponding end texts
        save_cropped_section(pdf_document, part_number, start_page, end_page, output_folder, start_texts, end_texts)
        part_number += 1

    pdf_document.close()

# Usage
pdf_path = 'testocr.pdf'
output_folder = 'output'

# Define start texts with corresponding end texts
_0 = [
        (["Schedule K-1 "],
        ["For Paperwork Reduction Act Notice, see the Instructions for Form 1065."])
    ]

_1 =  [
        (["Credits, etc.—International"],
        ["For Paperwork Reduction Act Notice, see the Instructions for Form 1065."])
    ]
    

_2 = [
        (["Check box(es) for additional specified attachments. See instructions."],
        ["13. Other international items"])
    ]

_3 = [
        (["Foreign Tax Credit Limitation","Foreign Tax Credit Limitation (continued)"],
        [
            "Other Information for Preparation of Form 1116 or 1118",
            "Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDI)",
            "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",
            "Distributions From Foreign Corporations to Partnership",
            "Information Regarding Passive Foreign Investment Companies (PFICs)",
            "Partner’s Interest in Foreign Corporation Income (Section 960)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_4 = [
        (["Other Information for Preparation of Form 1116 or 1118"],
        [
            "Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDI)",
            "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",
            "Distributions From Foreign Corporations to Partnership",
            "Information Regarding Passive Foreign Investment Companies (PFICs)",
            "Partner’s Interest in Foreign Corporation Income (Section 960)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_5 = [
        (["Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDI) "],
        [
            "Distributions From Foreign Corporations to Partnership",
            "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",
            "Information Regarding Passive Foreign Investment Companies (PFICs)",
            "Partner’s Interest in Foreign Corporation Income (Section 960)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_6 = [
        (["Distributions From Foreign Corporations to Partnership"],
        [
            "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",
            "Information Regarding Passive Foreign Investment Companies (PFICs)",
            "Partner’s Interest in Foreign Corporation Income (Section 960)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_7 = [
        (["Information on Partner’s Section 951(a)(1) and Section 951A Inclusions"],
        [
            "Information Regarding Passive Foreign Investment Companies (PFICs)",
            "Partner’s Interest in Foreign Corporation Income (Section 960)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_8 = [
        (["Information Regarding Passive Foreign Investment Companies (PFICs)"],
        [
            "Partner’s Interest in Foreign Corporation Income (Section 960)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_9 = [
        (["Partner’s Interest in Foreign Corporation Income (Section 960)", "Partner’s Interest in Foreign Corporation Income (Section 960) (continued)" ],
        [
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_10 = [ 
        (["Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) "],
        [
            "Foreign Partner’s Character and Source of Income and Deductions ",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_11 = [(["Foreign Partner’s Character and Source of Income and Deductions "],
        [
            "Schedule K-3 (Form 1065) ",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]

_13 =   [
        (["Foreign Partner’s Distributive Share of Deemed Sale Items on Transfer of Partnership Interest"],
        [
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]


split_pdf_by_section_ranges(pdf_path, output_folder +"/0", _0)

split_pdf_by_section_ranges(pdf_path, output_folder +"/1", _1)

split_pdf_by_section_ranges(pdf_path, output_folder +"/2", _2)

split_pdf_by_section_ranges(pdf_path, output_folder +"/3", _3)

split_pdf_by_section_ranges(pdf_path, output_folder +"/4", _4)

split_pdf_by_section_ranges(pdf_path, output_folder +"/5", _5)

split_pdf_by_section_ranges(pdf_path, output_folder +"/6", _6)

split_pdf_by_section_ranges(pdf_path, output_folder +"/7", _7)

split_pdf_by_section_ranges(pdf_path, output_folder +"/8", _8)

split_pdf_by_section_ranges(pdf_path, output_folder +"/9", _9)

split_pdf_by_section_ranges(pdf_path, output_folder +"/10", _10)

split_pdf_by_section_ranges(pdf_path, output_folder +"/11", _11)

split_pdf_by_section_ranges(pdf_path, output_folder +"/13", _13)
"""
    ,
    ,
    ,
    ,
    ,
    ,
    ,
    [
        ,
    [
        ["Section 871(m) Covered Partnerships"],
        [
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ]
    ],
  """