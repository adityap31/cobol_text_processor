import os
import re
import json


def fetch_filename(line):
    """
      Get a line and returns the file name and component name.

    Parameters
    ----------
    line: str
        A SELECT line from COBOL FILE-CONTROL.

    Returns
    -------
    called_name: str
        A flat file name SELECTED in the COBOL FILE-CONTROL.
    dd_name: str
        A ASSIGNED name given to the SELECTED flat file [Data Defination].

    Exception
    ---------
    error: str
        Print and Return Exception
    """
    try:
        # called_name = line[18:48].strip()
        # dd_name = line[55:].strip()

        line = line.split(" ")
        called_name = line[1]
        dd_name = line[3]

        if dd_name.startswith("UT-S-"):
            dd_name = dd_name.replace("UT-S-", "")

        if dd_name.endswith("."):
            dd_name = dd_name.replace(".", "")

        return called_name, dd_name

    except Exception as error:
        print(error)
        return str(error)


def process_cobol_file(file_path):
    """
      Get the file path and return called_name, dd_name, access_mode within a dictionary.

          Parameters
    ----------
    file_path: str
        A location of the cobol file

    Returns
    -------
    complete_details: dict
        A dictionary with details of file operation through the COBOL code.  
    """

    num_of_lines = sum(1 for line in open(file_path))

    current_line = 0
    OPENED_FILES = []

    details = {}
    complete_details = []

    with open(file_path) as input_data:
        for line in input_data:
            current_line += 1
            cleaned_line = line.strip()
            regex_line = re.search("FILE-CONTROL", cleaned_line)
            if regex_line and regex_line.start() == 7 and regex_line.end() == 19:
                break

        for line in input_data:
            current_line += 1
            if "SKIP" in line:
                break

        new_line = []

        for line in input_data:
            current_line += 1

            if "EJECT" in line:
                continue

            if "DATA DIVISION" in line:
                break

            select_line = line[6:].strip().split(" ")
            select_line = list(filter(("").__ne__, select_line))

            new_line = new_line + select_line

            if len(new_line) == 4:
                line = " ".join(new_line)
                new_line = []

                if re.search("SELECT", line):
                    control = {"file_name": "",
                               "component_name": "",
                               "called_name": "",
                               "component_type": "COBOL",
                               "comments": "",
                               "step_name": "",
                               "called_type": "FILE",
                               "dd_name": "",
                               "access_mode": "FILE NOT FOUND",
                               "calling_app_name": "",
                               "called_app_name": "",
                               "temp_file_name": ""
                               }

                    called_name, dd_name = fetch_filename(line)

                    control["file_name"] = file_path.split("\\")[-1]
                    control["component_name"] = file_path.split("\\")[-1][:-4]
                    control["called_name"] = called_name
                    control["dd_name"] = dd_name

                    details.update({called_name: control})

            elif len(new_line) < 4:
                continue

            cleaned_line = line.strip()
            regex_line = re.search("DATA DIVISION", cleaned_line)

            if regex_line and regex_line.start() == 7 and regex_line.end() == 20:
                break

        lines_list = ""
        flag = True

        # SECTION TO GET INPUT MODES
        while flag == True:
            for line in input_data:
                current_line += 1
                regex_line = re.search("OPEN", line)
                if regex_line:
                    trimmed_line = line[6:].strip()
                    if trimmed_line.startswith("OPEN"):
                        lines_list += trimmed_line + "\n"
                        break

            for line in input_data:
                current_line += 1
                trimmed_line = line[6:].strip()
                lines_list += trimmed_line.replace(".", "") + "\n"
                if trimmed_line.endswith("."):
                    break

            if current_line == num_of_lines:
                flag = False

        file_operations = []

        for line in lines_list.split("\n"):
            words = line.split()
            if len(words) == 3:
                action = words[0]
                mode = words[1]
                f_name = words[2]
                file_operations.append((action, mode, f_name))
            if len(words) == 2:
                mode = words[0]
                f_name = words[1]
                file_operations.append((action, mode, f_name))
            if len(words) == 1:
                f_name = words[0]
                file_operations.append((action, mode, f_name))

            OPENED_FILES.append(f_name)

        for operation in file_operations:
            faction, fmode, fname = operation[0], operation[1], operation[2]

            oper_dict = details[fname]
            oper_dict["access_mode"] = fmode
            complete_details.append(oper_dict)

        for key, val in details.items():
            if key not in OPENED_FILES:
                complete_details.append(val)

    return complete_details
