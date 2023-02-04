

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

dictionary = parse("FW_1238.conf")