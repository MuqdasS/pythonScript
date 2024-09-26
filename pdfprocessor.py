#for extract pdf
from PIL import Image
import io
import os
from difflib import SequenceMatcher

#for split pdf
from fuzzywuzzy import fuzz
import sys

#for both
import fitz
import pytesseract
import os

poppler_path = r"C:\Program Files\Release-24.07.0-0\poppler-24.07.0\Library\bin" 
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

""" Class for extracting SCANNED IMAGE PDFs to text based PDFs (of the same table format) so we can then split it using SplitPdf
*** IF ALREADY TEXT BASED THE PDF WILL BE SKIPPED FROM THIS CLASS. ***
"""

class ExtractPdf:
    def __init__(self, scanned_pdf_path, output_folder, output_name, poppler_path):
        """
        Initialize the ExtractPdf class with necessary parameters.
        
        :param scanned_pdf_path: Path to the scanned PDF file.
        :param output_folder: Directory where output files will be saved.
        :param output_name: Base name for output files (without extension).
        :param poppler_path: Path to Poppler (if needed).
        """
        self.scanned_pdf_path = scanned_pdf_path
        self.output_folder = output_folder
        self.output_name = output_name
        self.poppler_path = poppler_path
        
        self.ocr_pdf_path = os.path.join(self.output_folder, f"{self.output_name}.pdf")
        self.output_text_path = os.path.join(self.output_folder, f"{self.output_name}.txt")

    def convert_scanned_to_text_pdf(self):
        """
        Convert a scanned PDF to a text-based PDF using OCR or skip if already text-based.
        """
        # Check if OCR PDF already exists
        if os.path.exists(self.ocr_pdf_path):
            print(f"Skipping OCR conversion. The file {self.ocr_pdf_path} already exists.")
            return  # Skip the conversion if the file exists
        
        print("Extracting PDF using OCR...")

        try:
            scanned_doc = fitz.open(self.scanned_pdf_path)
            ocr_doc = fitz.open()  # Create a new blank PDF

            for page_number in range(len(scanned_doc)):
                page = scanned_doc.load_page(page_number)
                pix = page.get_pixmap(dpi=300)  # High DPI for better OCR results
                image = Image.open(io.BytesIO(pix.tobytes()))

                # Perform OCR to extract the text-based version of the page
                ocr_result = pytesseract.image_to_pdf_or_hocr(image, extension='pdf')
                # Create a new PDF page from OCR result
                ocr_page = fitz.open("pdf", ocr_result)
                ocr_doc.insert_pdf(ocr_page)  # Insert OCR page into the new PDF

            ocr_doc.save(self.ocr_pdf_path)
            print(f"OCR PDF saved as: {self.ocr_pdf_path}")
        except Exception as e:
            print(f"Error during PDF conversion: {e}")
        finally:
            scanned_doc.close()
            ocr_doc.close()

    def extract_text_blocks(self):
        """
        Extract all text blocks from the OCR PDF and save them to a text file for inspection.
        """
        # Check if output text file already exists
        if os.path.exists(self.output_text_path):
            print(f"Skipping text extraction. The file {self.output_text_path} already exists.")
            return  # Skip extraction if the file exists
        
        print("\nExtracting text blocks from the OCR PDF...")
        
        doc = fitz.open(self.ocr_pdf_path)
        
        try:
            with open(self.output_text_path, 'w', encoding='utf-8') as text_file:
                for page_number in range(len(doc)):
                    page = doc.load_page(page_number)
                    blocks = page.get_text("blocks")  # Extract text blocks
                    
                    text_file.write(f"\n--- Page {page_number + 1} ---\n")
                    for block in blocks:
                        text = block[4]  # The text content of the block
                        text_file.write(text.strip() + "\n")  # Write the text block content to file

            print(f"Extracted text saved to: {self.output_text_path}")

        except Exception as e:
            print(f"Error during text extraction: {e}")

        finally:
            doc.close()



""" Class for splitting the output selectable ocr pdf into sections for the K3 Tax Document"""
class SplitPdf:
    def __init__(self, pdf_document, output_folder):
        self.pdf_document = fitz.open(pdf_document)
        self.output_folder = output_folder
 
        """ Start and end texts to split by section - if start has more than one value it will iterate until value found"""
        self.K1_form = [
            (["Schedule K-1 "],
            ["For Paperwork Reduction Act Notice, see the Instructions for Form 1065."])
        ]
 
        self.K3_title_page =  [
                (["Credits, etc.—International", "Credits, etc.-International ", "Credits, etc. - International"],
                ["For Paperwork Reduction Act Notice, see the Instructions for Form 1065."])
            ]
           
 
        self._1 = [
                (["Check box(es) for additional specified attachments. See instructions."],
                ["13. Other international items"])
            ]
 
        self._2 = [
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
 
        self._3 = [
            (["Other Information for Preparation of Form 1116 or 1118", "Other Information for Preparation of Form 1116 or 1118 (continued)"],
            [
            "Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDII)",
                "Distributions From Foreign Corporations to Partnership",
                "Information on Partner’s Section 951(a)(1) and Section 951A Inclusions",        
                "Information Regarding Passive Foreign Investment Companies (PFICs)",
                "Information Regarding Passive Foreign Investment Companies (PFICs) (continued)",
                "Partner’s Interest in Foreign Corporation Income (Section 960) ",
                "Partner’s Interest in Foreign Corporation Income (Section 960) (continued)",
                "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
                "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) (continued)",
                "Foreign Partner’s Character and Source of Income and Deductions",
                "Foreign Partner’s Character and Source of Income and Deductions (continued)",
                "Section 871(m) Covered Partnerships",
                "Reserved for Future Use",
                "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
            ])
        ]
 
        self._4 = [
                (["Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDII) ", "Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDI) "],
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
 
        self._5 = [
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
 
        self._6 = [
            (["Information on Partner’s Section 951(a)(1) and Section 951A Inclusions", "Information Regarding Passive Foreign Investment Companies (PFICs) (continued)"],
            [
                "Information Regarding Passive Foreign Investment Companies (PFICs)",
                "Information Regarding Passive Foreign Investment Companies (PFICs) (continued)",
                "Partner’s Interest in Foreign Corporation Income (Section 960) ",
                "Partner’s Interest in Foreign Corporation Income (Section 960) (continued)",
                "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
                "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) (continued)",
                "Foreign Partner’s Character and Source of Income and Deductions",
                "Foreign Partner’s Character and Source of Income and Deductions (continued)",
                "Section 871(m) Covered Partnerships",
                "Reserved for Future Use",
                "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
            ])
        ]
 
        self._7 = [
        (["Information Regarding Passive Foreign Investment Companies (PFICs)", "Information Regarding Passive Foreign Investment Companies (PFICs) (continued)"],
        [
           "Partner’s Interest in Foreign Corporation Income (Section 960) ",
            "Partner’s Interest in Foreign Corporation Income (Section 960) (continued)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
            "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) (continued)",
            "Foreign Partner’s Character and Source of Income and Deductions",
            "Foreign Partner’s Character and Source of Income and Deductions (continued)",
            "Section 871(m) Covered Partnerships",
            "Reserved for Future Use",
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
        ])
    ]
 
        self._8 = [
            (["Partner’s Interest in Foreign Corporation Income (Section 960)", "Partner’s Interest in Foreign Corporation Income (Section 960) (continued)" ],
            [
                "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A)",
                "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) (continued)",
                "Foreign Partner’s Character and Source of Income and Deductions",
                "Foreign Partner’s Character and Source of Income and Deductions (continued)",
                "Section 871(m) Covered Partnerships",
                "Reserved for Future Use",
                "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
            ])
        ]
 
        self._9 = [
            (["Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) ", "Partner’s Information for Base Erosion and Anti-Abuse Tax (Section 59A) (continued)"],
            [
                "Foreign Partner’s Character and Source of Income and Deductions ",
                "Foreign Partner’s Character and Source of Income and Deductions (continued) ",
                "Section 871(m) Covered Partnerships",
                "Reserved for Future Use",
                "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets."
            ])
            ]
 
        self._10 =[
            (["Foreign Partner’s Character and Source of Income and Deductions ", "Foreign Partner’s Character and Source of Income and Deductions (continued) "],
            ["Section 871(m) Covered Partnerships",
                "Reserved for Future Use",
                "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gainassets."
            ])
        ]
 
        self._11 = [
            (["Section 871(m) Covered Partnerships"],
            [
                "Reserved for Future Use"
            ])
        ]  
 
        #We don't use section 12 so skipped
       
        self._13 =   [
        (["Foreign Partner’s Distributive Share of Deemed Sale Items on Transfer of Partnership Interest", "Total ordinary gain (loss) that would be recognized on the deemed sale of section 751 property"],
        [
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gainassets", "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gain assets"
        ])
        ]
 
    def extract_text_with_coords(self, page):
        """
        Extracts text blocks and their coordinates from a PDF page.
        """
        text_instances = []
        blocks = page.get_text("blocks")
        #print(f"Extracted {len(blocks)} blocks on page {page.number}")
       
        for block in blocks:
            block_text, block_rect = block[4], block[:4]
            if block_text.strip():
                text_instances.append((block_text, block_rect))
                #print(f"Text: {block_text.strip()}, Coords: {block_rect}")
        return text_instances
 
    def find_exact_match(self, text, target_texts):
        """Search for an exact match in the list of target texts"""
        return any(target_text in text for target_text in target_texts)
 
    def find_fuzzy_match(self, text, target_texts, threshold=90):
        """Search for fuzzy match (used if exact match not found)"""
        for target_text in target_texts:
            ratio = fuzz.ratio(target_text.lower(), text.lower())
 
            if ratio >= threshold:
                print(f"Fuzzy match found with score {ratio}: {text} -> {target_text}")
                return True
        return False
 
    def find_section_ranges(self, start_texts_with_multiple_ends):
        total_pages = len(self.pdf_document)
        ranges = []
   
        for start_texts, end_texts in start_texts_with_multiple_ends:
            start_page = None
            end_page = None
            potential_end_page = None  # Track if we hit "Reserved for Future Use" but don't act on it immediately
           
            #go through each page, checking extracted text for matches with each phrase (trying exact, then fuzzy matching for more accuracy)
            for page_number in range(total_pages):
                page = self.pdf_document.load_page(page_number)
                text_blocks = self.extract_text_with_coords(page)
 
                for text, _ in text_blocks:
                    if start_page is None and self.find_exact_match(text, start_texts):
                        start_page = page_number
                        print(f"Found exact start text on page {start_page}")
 
                    elif start_page is None and self.find_fuzzy_match(text, start_texts):
                        start_page = page_number
                        print(f"Fuzzy matched start text on page {start_page}")
                   
                    if start_page is not None:
                        # If we find a "Reserved for Future Use", mark this as potential end but continue looking
                        if self.find_exact_match(text, ["Reserved for Future Use"]):
                            potential_end_page = page_number
                            print(f"Found potential 'Reserved for Future Use' on page {potential_end_page}")
                       
                        # If we find a new section, stop at that instead of "Reserved for Future Use"
                        if self.find_exact_match(text, end_texts):
                            end_page = page_number
                            print(f"Found exact end text on page {end_page}")
                            break
                        elif self.find_fuzzy_match(text, end_texts):
                            end_page = page_number
                            print(f"Fuzzy matched end text on page {end_page}")
                            break
           
            if start_page is not None and (end_page is not None or potential_end_page is not None):
                # Use the actual end if found, or fallback to "Reserved for Future Use"
                final_end_page = end_page if end_page is not None else potential_end_page
                if start_page <= final_end_page:
                    ranges.append((start_texts, start_page, final_end_page))
            else:
                print(f"Could not find valid range for start '{start_texts}' and end texts {end_texts}")
        return ranges
 
    def crop_page(self, page, start_texts, end_texts):
        """
        Crops a page from the first found start_text to the first found end_text.
        """
        text_instances = self.extract_text_with_coords(page)
        crop_boxes = []
        cropping = False
       
        for text, rect in text_instances:
            # Try exact match first
            if self.find_exact_match(text, start_texts):
                cropping = True
                crop_boxes.append(rect)
            # Fuzzy match fallback for start_texts
            elif self.find_fuzzy_match(text, start_texts):
                cropping = True
                crop_boxes.append(rect)
 
            if cropping:
                crop_boxes.append(rect)
 
            # Try exact match for end_texts once cropping starts
            if self.find_exact_match(text, end_texts):
                cropping = False
                crop_boxes.append(rect)
                break
            # Fuzzy match fallback for end_texts
            elif self.find_fuzzy_match(text, end_texts):
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
 
    def save_cropped_section(self, part_number, start_page, end_page, start_texts, output_folder, end_texts):
        """
        Saves a cropped section of the PDF to a new file with part number.
        """
        output_pdf = fitz.open()
 
        for page_number in range(start_page, end_page + 1):
            page = self.pdf_document.load_page(page_number)
            cropped_pixmap = self.crop_page(page, start_texts, end_texts)
            if cropped_pixmap:
                new_page = output_pdf.new_page(width=cropped_pixmap.width, height=cropped_pixmap.height)
                new_page.insert_image(new_page.rect, pixmap=cropped_pixmap)
                cropped_pixmap = None  # Release memory immediately
            else:
                print(f"Could not crop page {page_number} due to missing text match.")
       
        if len(output_pdf) > 0:
            section_filename = f"{part_number}.pdf"
            section_path = os.path.join(output_folder, section_filename)
            output_pdf.save(section_path)
            output_pdf.close()
            print(f"Section saved: {section_filename}")
        else:
            print(f"Warning: Section 'Part_{part_number}' has no pages to save.")
 
 
    """ MAIN CLASS - USE THIS TO ABSTRACT FUNCTIONALITY OF THE OTHERS """
    def split_pdf_by_section_ranges(self, addition_to_output_folder, start_texts_with_multiple_ends):
        # Ensure the output folder exists
        output_folder_path = os.path.join(self.output_folder, self.pdf_document.name)
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
       
        # Find pages for each start and end section
        ranges = self.find_section_ranges(start_texts_with_multiple_ends)
       
        part_number = 0
        for start_texts, start_page, end_page in ranges:
            end_texts = start_texts_with_multiple_ends[part_number][1]  # Get corresponding end texts
            self.save_cropped_section(addition_to_output_folder, start_page, end_page, start_texts, output_folder_path, end_texts)
            part_number += 1
 
        #self.pdf_document.close()
 
 



"""" Script execution instructions: 

argument 1: scanned pdf path 
argument 2: output folder
argument 3: ocr output name
"""

def main():
    if len(sys.argv) < 1:
        print("Usage: python pdfprocessor.py <scanned_pdf_path>")
        print("Example: python pdfprocessor.py 'path/to/scanned.pdf'")
        sys.exit(1)

    # Arguments
    scanned_pdf_path = sys.argv[1]
    output_folder = "output"
    ocr_output_name = os.path.splitext(os.path.basename(scanned_pdf_path))[0] + "_EXTRACTED"

    # Check if the scanned PDF exists
    if not os.path.isfile(scanned_pdf_path):
        print(f"Error: The scanned PDF '{scanned_pdf_path}' does not exist.")
        sys.exit(1)


    # Create an instance of the PDF extractor
    pdf_extractor = ExtractPdf(scanned_pdf_path, output_folder, ocr_output_name, poppler_path)

    # Extract PDF to text
    pdf_extractor.convert_scanned_to_text_pdf()

    # Get OCR text output to txt for checking
    pdf_extractor.extract_text_blocks()
    
    # Path to extracted PDF
    extracted_pdf_path = pdf_extractor.ocr_pdf_path

    # Create an instance of the PDF splitter
    pdf_splitter = SplitPdf(extracted_pdf_path, output_folder)

    # Sections and corresponding folder names
    sections = {
        "K1": pdf_splitter.K1_form,
        "K3 Title Page": pdf_splitter.K3_title_page,
        "Part 1": pdf_splitter._1,
        "Part 2": pdf_splitter._2,
        "Part 3": pdf_splitter._3,
        "Part 4": pdf_splitter._4,
        "Part 5": pdf_splitter._5,
        "Part 6": pdf_splitter._6,
        "Part 7": pdf_splitter._7,
        "Part 8": pdf_splitter._8,
        "Part 9": pdf_splitter._9,
        "Part 10": pdf_splitter._10,
        "Part 11": pdf_splitter._11,
        "Part 13": pdf_splitter._13
    }

    # Split each section in the extracted PDF
    for file_name_addition, start_end in sections.items():
        print(f"\nStarting section '{file_name_addition}'...")
        pdf_splitter.split_pdf_by_section_ranges(file_name_addition, start_end)

if __name__ == "__main__":
    main()