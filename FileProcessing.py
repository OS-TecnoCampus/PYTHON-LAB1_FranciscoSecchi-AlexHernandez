import os
import re
import PyPDF2
from PyPDF2.generic import RectangleObject
from fpdf import FPDF


def parse(file_name):
    dict = {}
    current_config = None
    current_edit = None
    with open(file_name, "r") as f:
        lines = f.readlines()
        for line in lines:
            line = line.strip()
            if line.startswith("#"):
                current_config = line.split("=")[0][1:]
                value = re.split("[=-]|:", line)[1:]
                dict[current_config] = value
            elif line.startswith("config"):
                current_edit = None
                current_config = " ".join(line.split(" ")[1:])
                # print(current_config)
                dict[current_config] = {}
            elif line.startswith("edit"):
                current_edit = line.split(" ")[1].strip("\"")
                # print(current_edit)
                dict[current_config][current_edit] = {}
            elif line.startswith("set"):
                key = line.split(" ")[1].strip("\"")
                # print(key)
                value = line.split(" ")[2:]
                # print(value)
                if current_edit is None:
                    dict[current_config][key] = value
                else: 
                    dict[current_config][current_edit][key] = value
            elif line.startswith("next"):
                current_edit = None
            # print(current_config + ":  " +str(dict[current_config]))
    return dict

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
        self.add_page()
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10,"Índex",0,1)
        tab_width = [0, 10, 20]

        for section in self.sections:
            tabs = tab_width[section[1]-1]
            # link = self.add_link(section[3], 0, section[2])
            self.cell(tabs, 10, section[0], ln=0)
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
        self.set_fill_color(255, 255, 255)
        self.set_draw_color(0, 0, 0)
        self.set_font('Helvetica', '', 12)
        self.set_margins(20,20)

    def list_strings(self, strings, space):
        self.set_margins(30,20)
        for string in strings:
            self.cell(0,7,chr(149)+"\t\t"+string,0,0)
            self.ln(space)
        self.reset_format()
    
    def add_table(self, widths, data):
        for row in data:
            for i,item in enumerate(row):
                self.cell(widths[i], 10, str(item), 1, 0, 'L', 1)
            self.ln()      
        self.ln(15)

    def add_headed_table(self, widths, data):
        self.ln(15)
        self.set_fill_color(255, 200, 60)
        self.set_draw_color(255, 200, 0)
        self.set_font('Arial', 'B')
        for i,item in enumerate(data[0]):
            self.cell(widths[i], 7, str(item), 1, 0, 'L', 1)
        self.ln()
        self.reset_format()  
        self.set_draw_color(255, 200, 0)
        for row in data[1:]:
            for i,item in enumerate(row):
                self.cell(widths[i], 10, str(item), 1, 0, 'L', 1)
            self.ln()    
        self.reset_format()  
        self.ln(15)

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
    pdf.create_index()
    pdf.output('index')
    return 'index'

def merge(pdf1, pdf2, name):
    merger = PyPDF2.PdfMerger()
    merger.merge(position=0, fileobj=pdf2)
    merger.merge(position=0, fileobj=pdf1)
    merger.write(name)
    os.remove(pdf1)
    os.remove(pdf2)
    return name

def get_data(final, config, keys, values=0, edits=None, include=False):
    temp = dict[config] if edits is None else edits 
    for y,edit in enumerate(temp):
        row = []
        if(include):
            row.append(edit)
        for i,key in enumerate(keys):
            try:
                row.append(dict[config][edit][key][values[i]].strip("\""))
            except KeyError:
                row.append("")
        final.append(row)
    return final


dict = parse("FW_1238.conf")

frontpage = front_page()
content = PDF()
content.add_page()
content.reset_format()
version = dict["config-version"][0][3:]
# 1.
content.add_section('1. Introducció', 1)
# 1.1
content.add_section('1.1. Descripció', 2)
content.write(7,"El present document descriu la configuració realitzada en el dispositiu Fortigate-"+version+" de Fortinet "+
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
content.list_strings(strings, 10)
# 1.3

# 2.
content.add_section("2. Configuració del Dispositiu", 1)
content.write(7, "A continuació es detalla la configuració del disposiut Fortigate-"+version+".")
# 2.1
content.ln(15)
content.add_section("2.1 Dispositiu", 2)
widths = [40, 100]
data = [["Marca-Model", "FortiGate "+version], 
        ["OS/Firmware", "v"+dict["config-version"][1]+","+dict["config-version"][3]+" ("+dict["config-version"][4]+")"],
        ["S/N",""]]
content.add_table(widths, data)
# 2.2
content.add_section("2.2. Credencials d'accés", 2)
content.set_font('Helvetica', 'B')
content.cell(h= 7, txt="Accés: ", )
content.reset_format()
content.cell(0, 7, "https://10.132.4.254:"+ dict["system global"]["admin-sport"][0])
content.ln(7)
content.set_font('Helvetica', 'B')
content.cell(h= 7, txt="Usuari: ")
content.reset_format()
content.cell(0, 7, "admin")
content.ln(7)
content.set_font('Helvetica', 'B')
content.cell(h= 7, txt="Password: ")
content.reset_format()
content.cell(0, 7, "dfAS34")
content.ln(7)
content.set_font('Helvetica', 'B')
content.cell(h= 7, txt="Restriccions d'accés: ")
content.reset_format()
content.cell(0, 7, "xarxes "
                    +dict["system admin"]["admin"]["trusthost1"][0]+", "
                    +dict["system admin"]["admin"]["trusthost2"][0]+", "
                    +dict["system admin"]["admin"]["trusthost3"][0])
content.ln(15)
# 2.3
content.add_section("2.3. General", 2)
content.write(7,"El dispositiu està configurat en mode NAT, és a dir, es separen vàries xarxes a nivell tres d'enrutament.")
content.ln(15)
content.cell(h= 7, txt="DNS: ")
content.ln(7)
strings = ["Servidor Primari: "+dict["system dns"]["primary"][0],
            "Servidor Secundari: "+dict["system dns"]["secondary"][0],
            "Nom del domini Local: "+dict["system dns"]["domain"][0]]
content.list_strings(strings, 7)
content.ln(7)
# 2.4
content.add_section("2.4. Interfícies", 2)
content.write(7, "El dispositiu instal·lat disposa d'una taula de polítiques de connexió per tal de definir el comportament del mateix per cada una de les connexions tractades.")

widths = [35,30,60,0]
data = [["Interficie", "Alias", "Address/FQDN","DHCPRelay"]]

temp = dict["system interface"]
for i,edit in enumerate(temp):
    if(i>3):
        break
    row = []
    row.append(edit)
    row.append(temp[edit]["alias"][0].strip("\""))
    row.append(temp[edit]["ip"][0])
    try:
        row.append(temp[edit]["dhcp-relay-ip"][0].strip("\""))
    except KeyError:
        row.append("-")
    data.append(row)

content.add_headed_table(widths, data)
# 2.5.
iter = iter(dict["router static"])
content.add_section("2.5. Taula d'enrutament", 2)
content.write(7,"S'ha definit "+ str(len(dict["router static"]))+" default gw per permetre la sortida per les dues sortides a internet de la organització. Per defecte el tràfic sortirà a través del GW "+
                dict["router static"][next(iter)]["gateway"][0]+" (prioritat menor) i en cas de caiguda de la línia es redirigirà el tràfic a través del GW "+
                dict["router static"][next(iter)]["gateway"][0])

widths = [40,30,30,0]
data = [["Xarxa Destí", "GW", "Interficie", "Prioritat"]]
keys = ["gateway","device","priority"]
data = get_data(data, "router static", keys, [0,0,0])
for i in range(1, len(data)):
    data[i].insert(0, "0.0.0.0/0.0.0.0")
content.add_headed_table(widths, data)

content.write(7, "S'ha definit una sèrie de Health-checks de ping a través de les interfícies wan per detectar la caiguda de les línies de comunicacions.")

widths = [35,30,30,20,20,0]
data = [["Servidor Destí", "GW", "Interficie", "Interval", "failtime", "recovery"]]
keys = ["server","gateway-ip","srcintf","interval","failtime","recoverytime"]
data = get_data(data, "system link-monitor", keys, [0,0,0,0,0,0])
content.add_headed_table(widths, data)
# 2.6.
content.add_section("2.6. Objectes Adreces del Firewall", 2)
content.write(7, "El dispositiu actualment te vinculats determinats objectes (noms descriptius) a adreces IP per tal de facilitar la seva utilització en el sistema.")

widths = [40,25,50,30,0]
data = [["Name", "Category", "Address/FQDN", "Interface", "Type*"]]
edits = ["inside_srv","inside_wrk", "cloud1", "cloud2", "srv-demeter", "srv-devrepo","srv-nebulaz","vpn-net"]
keys = ["-","subnet","-","type"]
data = get_data(data, "firewall address", keys, [0,0,0,0], edits, True)
for i in data[1:]:
    i[1] = "Address"
    i[3] = "Any"
    i[4] = "Range" if i[4] == "iprange" else "Subnet" 
content.add_headed_table(widths, data)
# 2.7.
content.add_section("2.7. Objectes Serveis", 2)
content.write(7, "El dispositiu configurat disposa de serveis predeterminats per defecte establerts per FortiNet i addicionalment te introduïts serveis personalitzats. \nEls serveis predeterminats són:")

widths = [40,50,30,30,0]
data = [["Nom del Servei", "Categoria", "Ports TCP", "Ports UDP", "Protocol"]]
keys = ["category","tcp-portrange","udp-portrange","protocol"]
data = get_data(data, "firewall service custom", keys, [0,0,0,0], include=True)
 
content.add_headed_table(widths, data)


merged = merge(front_page(), index(content.sections), 'merg')
content.output('content')
pdf_final = merge(merged, 'content', 'TCM_Report')