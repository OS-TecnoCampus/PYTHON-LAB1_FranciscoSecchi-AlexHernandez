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
                current_config = line.split("=")[0][1:]
                print(current_config)
                value = line.split("=")[1:]
                print(value)
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
    def __init__(self):
        super().__init__()
        self.sections = []
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

    def create_index(self):
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10,"Índex",0,1)
        tab_width = [0, 10, 20]

        for section in self.sections:
            tabs = tab_width[section[1]-1]
            link = self.add_link(section[3], 0, section[2])
            self.cell(tabs, 10, section[0], ln=0, link=link)
            self.ln()

    def add_section(self, txt, priority):
        self.set_text_color(255, 180, 0)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 7,txt,0,1)
        self.ln()
        self.reset_format()
        self.sections.append((txt, priority, self.page_no(), self.get_y()))
    
    def reset_format(self):
        self.set_text_color(0, 0, 0)
        self.set_font('Helvetica', '', 12)
        self.set_margins(20,20)

    def list_strings(self, strings):
        self.set_margins(30,20)
        for string in strings:
            self.cell(0,7,chr(149)+"\t\t"+string,0,0)
            self.ln(15)
        self.reset_format()

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
    pdf.write(3,"La informació continguda en aquest document pot ser de caràcter privilegiat y/o confidencial. Qualsevol"+
                    " disseminació, distribució o copia d,aquest document per qualsevol altre persona diferent als receptors"+
                    " originals queda estrictament prohibida. Si ha rebut aquest document per error, sis plau notifiquí"+
                    " immediatament al emissor i esborri qualsevol copia d'aquest document.")
    pdf.set_line_width(5)
    pdf.set_draw_color(255,165,0)
    pdf.line(20, 10, 20, 280)
    pdf.output('portada')
    return 'portada'

def index(sections):
    pdf = PDF()
    pdf.sections = sections
    pdf.add_page('P', 'A4')
    pdf.create_index()
    pdf.output('index')
    return 'index'

def merge(pdf1, pdf2, name):
    merger = PdfMerger()
    merger.merge(position=0, fileobj=pdf2)
    merger.merge(position=0, fileobj=pdf1)
    merger.write(name)
    os.remove(pdf1)
    os.remove(pdf2)
    return name


dictionary = parse("FW_1238.conf")

frontpage = front_page()
content = PDF()
content.add_page()
content.reset_format()

# 1.
content.add_section('1. Introducció', 1)
# 1.1
content.add_section('1.1. Descripció', 2)
content.write(7,"El present document descriu la configuració realitzada en el dispositiu Fortigate-"+dictionary["config-version"][0][3:6]+" de Fortinet "+
            "a la empresa TecnoCampus resultat de la substitució de un Firewall perimetral Cisco de "+
            "l'organització.")
# 1.2
content.ln(15)
content.add_section('1.2. Objectius', 2)
content.write(7, "El objectiu d'aquest document és la de formalitzar el traspàs d'informació al equip tècnic"+
                " responsable del manteniment de les infraestructures instal·lades. Aquesta informació fa"+
                " referencia al disseny, instal·lació i configuració dels dispositius i sistemes afectats per implementació.")
content.ln(15)
content.cell(0, 7, "La present documentació inclou:")
content.ln(15)
strings = ["Descripció general de les infraestructures instal·lades.",
            "Polítiques de filtratge de tràfic.", "Perfils de seguretat.", "Connexions Túnel."]
content.list_strings(strings)
# 1.3
content.add_page()
merged = merge(front_page(), index(content.sections), 'merg')
content.output('content')
pdf_final = merge(merged, 'content', 'TCM_Report')