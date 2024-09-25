import fitz        
import pytesseract
import os

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


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
                (["Credits, etc.—International"],
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
                (["Information on Partner’s Section 250 Deduction With Respect to Foreign-Derived Intangible Income (FDII) "],
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
                "Foreign Partner’s Character and Source of Income and Deductions",
                "Foreign Partner’s Character and Source of Income and Deductions (continued)",
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
 
        #change for future years
        self._11 = [
            (["Section 871(m) Covered Partnerships"],
            [
                "Reserved for Future Use"
            ]) 
        ]   

        #We don't use section 12 so skipped
        
        self._13 =   [
        (["Foreign Partner’s Distributive Share of Deemed Sale Items on Transfer of Partnership Interest"],
        [
            "Gain that would be recognized under section 897(g) on the deemed sale of section 1(h)(6) unrecaptured section 1250 gainassets"
        ])
        ]
 
    def extract_text_with_coords(self, page):
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

    def find_section_ranges(self, start_texts_with_multiple_ends):
        total_pages = len(self.pdf_document)
        ranges = []
        
        for start_texts, end_texts in start_texts_with_multiple_ends:
            start_page = None
            end_page = None
            
            for page_number in range(total_pages):
                page = self.pdf_document.load_page(page_number)
                text_blocks = self.extract_text_with_coords(page)

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

    def crop_page(self, page, start_texts, end_texts):
        """
        Crops a page from the first found start_text to the first found end_text.
        """
        text_instances = self.extract_text_with_coords(page)
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
        
        if len(output_pdf) > 0:
            section_filename = f"Part_{part_number}.pdf"
            section_path = os.path.join(output_folder, section_filename)
            output_pdf.save(section_path)
            output_pdf.close()
            print(f"Section saved: {section_filename}")
        else:
            print(f"Warning: Section 'Part_{part_number}' has no pages to save.")


    """ MAIN CLASS - USE THIS TO ABSTRACT FUNCTIONALITY OF THE OTHERS """
    def split_pdf_by_section_ranges(self, addition_to_output_folder, start_texts_with_multiple_ends):
        # Ensure the output folder exists
        output_folder_path = os.path.join(self.output_folder, self.pdf_document.name, addition_to_output_folder)
        if not os.path.exists(output_folder_path):
            os.makedirs(output_folder_path)
        
        # Find pages for each start and end section
        ranges = self.find_section_ranges(start_texts_with_multiple_ends)
        
        part_number = 0
        for start_texts, start_page, end_page in ranges:
            end_texts = start_texts_with_multiple_ends[part_number][1]  # Get corresponding end texts
            self.save_cropped_section(part_number, start_page, end_page, start_texts, output_folder_path, end_texts)
            part_number += 1

        #self.pdf_document.close()





"""Extract pdf"""

"""Split pdf"""
extracted_pdf_path = 'testocr.pdf'
extracted_output_folder = 'output'


pdf_splitter = SplitPdf(extracted_pdf_path, extracted_output_folder)

#sections and corresponding folder names
sections = {"K1": pdf_splitter.K1_form,  "K3 Title Page": pdf_splitter.K3_title_page, "Section 1": pdf_splitter._1, "Section 2": pdf_splitter._2, "Section 3": pdf_splitter._3, "Section 4": pdf_splitter._4, "Section 5": pdf_splitter._5, "Section 6": pdf_splitter._6, "Section 7": pdf_splitter._7, "Section 8": pdf_splitter._8, "Section 9": pdf_splitter._9, "Section 10": pdf_splitter._10, "Section 11": pdf_splitter._11, "Section 13": pdf_splitter._13}

#split each section in the extracted pdf
for file_name_addition, start_end in sections.items():
    pdf_splitter.split_pdf_by_section_ranges(file_name_addition, start_end)

    