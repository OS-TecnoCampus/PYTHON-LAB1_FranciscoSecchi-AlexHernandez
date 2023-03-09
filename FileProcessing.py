import os
import re
import PyPDF2
from fpdf import FPDF, XPos, YPos


def parse(lines):
    dict = {}
    current_config = None
    current_edit = None
    temp_lines = []
    for line in lines:
        line = line.strip()
        if line.startswith("#"):
            current_config = line.split("=")[0][1:]
            value = re.split("[=-]|:", line)[1:]
            dict[current_config] = value
        elif(len(temp_lines)>0):
            if line.startswith("next"):
                value = parse(temp_lines)
                key = temp_lines[0][7:].strip()
                dict[current_config][current_edit][key]=value[key]
                current_edit = None
                temp_lines = []
            else: temp_lines.append(line)
        elif line.startswith("config"):
            if current_edit is None:
                current_config = " ".join(line.split(" ")[1:])
                dict[current_config] = {}
            else: temp_lines.append(line)
            # print(current_config)
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
        # print("\n"+current_config + "-->  " +str(dict[current_config]))
    return dict

class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.sections = []
    def header(self):
        if self.page_no() >1:
            self.image('utils/logo.png', 150, 12, 35)
            self.set_font('Helvetica', '', 11)
            self.cell(0, 10,'Migració de la infraestructura de seguretat perimetral',0,align='L')
        self.ln(20)

    def footer(self):
        
        if self.page_no() >1:
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
        # Page number
            self.cell(0, 10, 'Pàgina %s | ' % self.page_no()+self.str_alias_nb_pages, 0, align='R')

    def create_index(self):
        self.add_page()
        self.set_font('Helvetica', 'B', 12)
        self.cell(0, 10,"Índex",0)
        tab_width = [0, 10, 20]

        for section in self.sections:
            tabs = tab_width[section[1]-1]
            # link = self.add_link(section[3], 0, section[2])
            self.cell(tabs, 10, section[0])
            self.ln()

    def add_section(self, txt, priority):
        self.set_text_color(255, 180, 0)
        self.set_font('Helvetica', 'B', 14)
        self.cell(0, 7,txt,0)
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
            self.cell(0,7,chr(149)+"\t\t"+string,0)
            self.ln(space)
        self.reset_format()
    
    def add_table(self, widths, data):
        for row in data:
            for i,item in enumerate(row):
                self.cell(widths[i], 10, str(item), 1, align='L', fill=1)
            self.ln()      
        self.ln(15)

    def add_headed_table(self, widths, data):
        self.ln(10)
        self.set_fill_color(255, 200, 60)
        self.set_draw_color(255, 200, 0)
        self.set_font('Arial', 'B')
        height = []
        for i in range(len(data)):
            height.append(0)
        for x,row in enumerate(data):
            height[x] = self.font_size_pt
            for i,item in enumerate(row):
                length = self.multi_cell(widths[i], self.font_size_pt, str(item), 1, 'L', 1, split_only=True)
                if(len(length)>1):
                    height[x] = self.font_size_pt * len(length)

        for i,item in enumerate(data[0]):
            self.multi_cell(widths[i], height[0], str(item), 1, 'L', 1, max_line_height=self.font_size_pt, new_x=XPos.RIGHT, new_y=YPos.TOP)
        self.ln(height[0]) 
        self.set_draw_color(255, 200, 0) 
        self.set_font('Arial', '')
        for x,row in enumerate(data[1:]):
            for i,item in enumerate(row):
                self.multi_cell(widths[i], height[x+1], str(item), 1, 'L', 0, max_line_height=self.font_size_pt, new_x=XPos.RIGHT, new_y=YPos.TOP)
            self.ln(height[x+1])    
        self.reset_format()  
        self.ln(15)

def front_page():
    pdf = PDF()
    pdf.add_page('P', 'A4')
    pdf.image('utils/logo.png', 110, 40)
    pdf.set_left_margin(30)
    pdf.set_font("Helvetica", size=28)
    pdf.ln(80)
    pdf.cell(0, 5, txt="Migració de la infraestructura de", align="L")
    pdf.ln()
    pdf.cell(0, 20, txt="seguretat perimetral per a", align="L")
    pdf.ln()
    pdf.cell(0, 20, txt="TecnoCampus", align="L")
    pdf.ln()
    pdf.ln()
    pdf.set_font("Helvetica", size=14)
    pdf.cell(0, 20, txt="Febrer, 2023", align="L")
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

def get_data(final, config, keys, values=None, edits=None, include=False, separator=""):
    temp = dict[config] if edits is None else edits 
    for edit in temp:
        row = []
        if(include):
            row.append(edit)
        for i,key in enumerate(keys):
            try:
                if(values is None):
                    v = ""
                    for value in range(len(dict[config][edit][key])):
                        v += dict[config][edit][key][value].strip("\"")+separator
                    row.append(v)
            except KeyError:
                row.append("")
        final.append(row)
    return final


with open("FW_1238.conf", "r") as f:
        lines = f.readlines()
        dict = parse(lines)

frontpage = front_page()
content = PDF()
content.add_page()
content.reset_format()

# 1.
content.add_section('1. Introducció', 1)
# 1.1
content.add_section('1.1. Descripció', 2)
content.write(7,"El present document descriu la configuració realitzada en el dispositiu Fortigate-"
                +dict["config-version"][1][3:]+" de Fortinet "+
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
content.list_strings(["Descripció general de les infraestructures instal·lades.",
                    "Polítiques de filtratge de tràfic.", 
                    "Perfils de seguretat.", "Connexions Túnel."], 10)
# 1.3
content.add_page()
content.add_section("1.3. Descripció general de les infraestructures", 2)
content.write(7, "Actualment la infraestructura te la següent distribució:")
content.image('utils/Infraestructura.png', 20, 70, 170, 140)
content.ln(170)
content.write(7, "En aquest esquema es pot veure com el firewall disposa actualment de dos connexions a internet (Port1 i Port4) que es connecten a través de diferents routers."
                +"\n\nLa infraestructura disposa de dos xarxes locals, la xarxa de servidors i la xarxa d'estacions de"
                +"treball.")

# 2.
content.add_page()
content.add_section("2. Configuració del Dispositiu", 1)
content.write(7, "A continuació es detalla la configuració del disposiut Fortigate-"
                    +dict["config-version"][1][3:]+".")

# 2.1
content.ln(15)
content.add_section("2.1 Dispositiu", 2)
widths = [40, 100]
data = [["Marca-Model", "FortiGate "+dict["config-version"][1][3:]], 
        ["OS/Firmware", "v"+dict["config-version"][2]+","+dict["config-version"][4]+" ("+dict["config-version"][5]+")"],
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
            "Nom del domini Local: "+dict["system dns"]["domain"][0].strip("\"")]
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
content.add_page()
iter = iter(dict["router static"])
content.add_section("2.5. Taula d'enrutament", 2)
content.write(7,"S'ha definit "+ str(len(dict["router static"]))+" default gw per permetre la sortida per les dues sortides a internet de la organització. Per defecte el tràfic sortirà a través del GW "+
                dict["router static"][next(iter)]["gateway"][0]+" (prioritat menor) i en cas de caiguda de la línia es redirigirà el tràfic a través del GW "+
                dict["router static"][next(iter)]["gateway"][0])

widths = [40,30,30,0]
data = [["Xarxa Destí", "GW", "Interficie", "Prioritat"]]
keys = ["gateway","device","priority"]
data = get_data(data, "router static", keys)
for i in range(1, len(data)):
    data[i].insert(0, "0.0.0.0/0.0.0.0")
content.add_headed_table(widths, data)

content.write(7, "S'ha definit una sèrie de Health-checks de ping a través de les interfícies wan per detectar la caiguda de les línies de comunicacions.")

widths = [35,30,30,20,20,0]
data = [["Servidor Destí", "GW", "Interficie", "Interval", "failtime", "recovery"]]
keys = ["server","gateway-ip","srcintf","interval","failtime","recoverytime"]
data = get_data(data, "system link-monitor", keys)
content.add_headed_table(widths, data)
# 2.6.
content.add_section("2.6. Objectes Adreces del Firewall", 2)
content.write(7, "El dispositiu actualment te vinculats determinats objectes (noms descriptius) a adreces IP per tal de facilitar la seva utilització en el sistema.")

widths = [30,20,60,20,0]
data = [["Name", "Category", "Address/FQDN", "Interface", "Type*"]]
edits = ["inside_srv","inside_wrk", "cloud1", "cloud2", "srv-demeter", "srv-devrepo","srv-nebulaz","vpn-net"]
keys = ["-","subnet","-","type"]
data = get_data(data, "firewall address", keys, edits=edits, include=True, separator="/")
for i in data[1:]:
    i[1] = "Address"
    i[3] = "Any"
    i[4] = "Range" if i[4] == "iprange" else "Subnet" 
content.add_headed_table(widths, data)
# 2.7.
content.add_section("2.7. Objectes Serveis", 2)
content.write(7, "El dispositiu configurat disposa de serveis predeterminats per defecte establerts per FortiNet i addicionalment te introduïts serveis personalitzats. \nEls serveis predeterminats són:")

widths = [45,50,30,30,0]
data = [["Nom del Servei", "Categoria", "Ports TCP", "Ports UDP", "Protocol"]]
keys = ["category","tcp-portrange","udp-portrange","protocol"]
data = get_data(data, "firewall service custom", keys, include=True)
content.add_headed_table(widths, data[:-2])
content.write(7, "Els serveis addicionals són:")
del data[1:-2]
for i in data:
    del i[4]
for i in data[1:]:
    i[1] = "Uncategorized"
content.add_headed_table(widths, data)

# 2.8.
content.add_section("2.8. NATs d'entrada /Virtual IPs)", 2)
content.write(7, "S'ha definit els següents NATs d'entrada (VIPs en nomenclatura Fortinet)")

widths = [30,45,40,30,0]
data = [["Name", "External IP Address/Range", "External Service Port", "Mapped IP Address/Range", "Map to Port"]]
keys = ["extintf","extip", "extport", "mappedip", "mappedport", "protocol"]
data = get_data(data, "firewall vip", keys, include=True)
for i in data[1:]:
    i[1] = i[1] +"/"+ i[2]
    i[3] = i[3] +"/"+ i[6]
    i[5] = i[5] +"/"+ i[6]
    del i[2]
    del i[-1]
content.add_headed_table(widths, data)

# 2.9
content.add_section("2.9. Polítiques de Firewall", 2)
content.write(7, "A continuació es mostren les polítiques de filtratge definides en el dispositiu Fortigate:")

widths = [7,15,15,20,20,10,12,13,13,14,15,15,10,10]
data = [["ID", "From", "To", "Source", "Destination", "Service", "Action", "AV", "Web Filter", "App Control", "IPS", "SSL Inspect", "Log", "NAT"]]
keys = ["srcintf","dstintf", "srcaddr", "dstaddr","groups", "service", "action", "av-profile", "webfilter-profile", "application-list", "ips-sensor", "ssl-ssh-profile", "logtraffic", "nat"]
data = get_data(data, "firewall policy", keys, include= True)
for i in data[1:7]:
    i[1] = i[1] +"("+ i[3]+")"
for i in data[1:]:
    i[2] = i[2] +" ("+ i[4]+")"
    i[3] = i[3] +" ("+ i[5]+")"
    del i[5]
data.append(["", "Any", "Any", "All", "All", "ALL", "Deny","","","","","","",""])
content.set_font_size(7)
content.set_margins(left=10,top=20 ,right=10)
content.add_headed_table(widths, data)

# 2.10.
content.add_section("2.10. Servei Antivirus", 2)
content.write(7, "El servei antivirus perimetral proveeix d'una base de dades automatitzada per assegurar la protecció davant de possible contingut de malware detectat a través de la navegació WEB."
                +"\nActualment el dispositiu te com el perfil d'antivirus activat "+
                list((dict["antivirus profile"]).keys())[-1]
                +"que detecta i neteja malware i possibles connexions a xarxes de Botnets.")
# 2.11
content.ln(15)
content.add_section("2.11. Servei de Filtrage Web", 2)
content.write(7, "El servei de filtratge de web, proveeix d'un servei de filtratge de contingut web a través dels protocols de navegació."
                +"\nActualment en el dispositiu s'ha definit el perfil "+
                list(dict["webfilter profile"])[-1]
                +"que actualment únicament genera logs de tot el tràfic de navegació web.")
# 2.12
content.ln(15)
content.add_section("2.12. Servei Application control", 2)
content.write(7, "El servei de Application Control realitza un filtratge a nivell d'aplicació per tal de bloquejar o filtrar determinades comunicacions d'aplicacions."
                +"\nEn el dispositiu s'ha activat el perfil "+
                list(dict["application list"])[-1]
                +" i s'ha configurat per a generar logs de totes les aplicacions utilitzades i bloqueja totes les connexions d'aplicacions típiques de BotNets.")
# 2.13
content.ln(15)
edit =dict["ips sensor"]
content.add_section("2.13. Servei Intrusion Protection", 2)
temp = dict["ips sensor"][list(dict["ips sensor"])[-1]]["entries"]["1"]
content.write(7, "El Servei de Intrusion Protection permet detectar possibles atacs de xarxa contra la infraestructura de la organització."
                +"\nEn el dispositiu s'ha activat el perfil UTM-IPS"
                +" en les polítiques de navegació web i s'han activat el comportament per defecte (bloqueig en cas necessari o monitorzació) de les signatures de tipus "
                +temp["location"][0] + ", de criticitat \""+ temp["severity"][1] + "\" i \""
                +temp["severity"][0]+ "\" que afectin a serveis de sistemes operatius"
                +temp["os"][0]+", "+temp["os"][1]+" i "+temp["os"][2]+".")


merged = merge(front_page(), index(content.sections), 'merg')
content.output('content')
pdf_final = merge(merged, 'content', 'TCM_Report')