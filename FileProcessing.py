from fpdf import FPDF

class PDF(FPDF):
    def header(self):
        if self.page_no() >1:
            self.image('utils/logo.png', 150, 12, 35)
            self.set_font('Arial', '', 11)
            self.cell(0, 10,'Migració de la infraestructura de seguretat perimetral',0,1,'L')
        # Line break
        self.ln(20)

    def footer(self):
        
        if self.page_no() >1:
            self.set_y(-15)
            self.set_font('Arial', 'I', 8)
        # Page number
            self.cell(0, 10, 'Pàgina %s | ' % self.page_no()+self.alias_nb_pages(), 0, 0, 'R')

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

def front_page():
    pdf_file.add_page('P', 'A4')
    pdf_file.image('utils/logo.png', 110, 40)
    pdf_file.set_left_margin(30)
    pdf_file.set_font("Arial", size=28)
    pdf_file.ln(80)
    pdf_file.cell(0, 5, txt="Migració de la infraestructura de", ln=1, align="L")
    pdf_file.cell(0, 20, txt="seguretat perimetral per a", ln=1, align="L")
    pdf_file.cell(0, 20, txt="TecnoCampus", ln=1, align="L")
    pdf_file.ln()
    pdf_file.set_font("Arial", size=14)
    pdf_file.cell(0, 20, txt="Febrer, 2023", ln=1, align="L")
    pdf_file.ln(65)
    pdf_file.set_font("Arial", "B", size=8)
    pdf_file.multi_cell(150,3,"\tLa informació continguda en aquest document pot ser de caràcter privilegiat y/o confidencial. Qualsevol"+
                            " \tdisseminació, distribució o copia d,aquest document per qualsevol altre persona diferent als receptors"+
                            " \toriginals queda estrictament prohibida. Si ha rebut aquest document per error, sis plau notifiquí"+
                            " \timmediatament al emissor i esborri qualsevol copia d,aquest document.",
                            align="J")
    pdf_file.set_line_width(5)
    pdf_file.set_draw_color(255,165,0)
    pdf_file.line(20, 10, 20, 280)

def create_index():
    pdf_file.add_page('P', 'A4')

dictionary = parse("FW_1238.conf")
pdf_file = PDF()
front_page()
pdf_file.add_page()
pdf_file.output('TCM_ReportPDF')



