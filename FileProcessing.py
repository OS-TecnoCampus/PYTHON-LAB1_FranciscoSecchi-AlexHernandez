import os
from PyPDF2 import PdfMerger
from fpdf import FPDF


def parse(file_name):
    dictionary = {}
    current_config = None
    current_edit = None
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                current_config = line.split("=")[0]
                value = line.split("=")[1:]
                dictionary[current_config] = value
            elif line.startswith("config"):
                current_edit = None
                current_config = " ".join(line.split(" ")[1:])
                dictionary[current_config] = {}
            elif line.startswith("edit"):
                current_edit = line.split(" ")[1].strip("\"")
                dictionary[current_config][current_edit] = {}
            elif line.startswith("set"):
                key = line.split(" ")[1].strip("\"")
                value = line.split(" ")[2:]
                if current_edit is None:
                    dictionary[current_config][key] = value
                else: 
                    dictionary[current_config][current_edit][key] = value
            elif line.startswith("next"):
                current_edit = None
    return dictionary

class PDF(FPDF):
    def header(self):
        if self.page_no() >1:
            self.image('utils/logo.png', 150, 12, 35)
            self.set_font('Helvetica', '', 11)
            self.cell(0, 10,'Migració de la infraestructura de seguretat perimetral',0,1,'L')
        # Line break
        self.ln(20)

    def footer(self):
        
        if self.page_no() >1:
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
        # Page number
            self.cell(0, 10, 'Pàgina %s | ' % self.page_no()+self.str_alias_nb_pages, 0, 0, 'R')

    def create_index(self, sections):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10,"Índex",0,1)

        for section in sections:
            self.cell(0, 10, section[0], 0, link=self.add_link(section[1]))
            self.cell(30, 10, str(section[1]), 0, 1)


def front_page():
    pdf = PDF()
    pdf.add_page('P', 'A4')
    pdf.image('utils/logo.png', 110, 40)
    pdf.set_left_margin(30)
    pdf.set_font("Helvetica", size=28)
    pdf.ln(80)
    pdf.cell(0, 5, txt="Migració de la infraestructura de", ln=1, align="L")
    pdf.cell(0, 20, txt="seguretat perimetral per a", ln=1, align="L")
    pdf.cell(0, 20, txt="TecnoCampus", ln=1, align="L")
    pdf.ln()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 20, txt="Febrer, 2023", ln=1, align="L")
    pdf.ln(65)
    pdf.set_font("Helvetica", "B", size=8)
    pdf.multi_cell(150,3,"\tLa informació continguda en aquest document pot ser de caràcter privilegiat y/o confidencial. Qualsevol"+
                            " \tdisseminació, distribució o copia d,aquest document per qualsevol altre persona diferent als receptors"+
                            " \toriginals queda estrictament prohibida. Si ha rebut aquest document per error, sis plau notifiquí"+
                            " \timmediatament al emissor i esborri qualsevol copia d,aquest document.",
                            align="J")
    pdf.set_line_width(5)
    pdf.set_draw_color(255,165,0)
    pdf.line(20, 10, 20, 280)
    return pdf

def merge(pdf1, pdf2):
    merger = PdfMerger()
    merger.merge(position=0, fileobj=pdf2)
    merger.merge(position=0, fileobj=pdf1)
    merger.write('TCM_ReportPDF')
    os.remove(pdf1)
    os.remove(pdf2)

sections = [("1.1 Introducció", 1), 
            ("1.2 Descripció", 2), 
            ("name 2.1", 3)]
dictionary = parse("FW_1238.conf")

frontpage = front_page()
content = PDF()
content.add_page()
content.create_index(sections)
content.add_page()
frontpage.output('portada')
content.output('contentPDF')

pdf_final = merge('portada', 'contentPDF')