"""This module handles all actions relating to fplka."""

import os

from robot_framework.sap.common import set_clipboard, export_file


def search_cases(session) -> tuple[tuple[str]]:
    """Search for udlignede cases with rykkerspærre.

    Args:
        session: The SAP session object.

    Returns:
        A tuple of forretningspartnere and a tuple of aftaler.
    """
    session.startTransaction("fplka")

    # Clear fp and aftale
    session.findById("wnd[0]/usr/ctxtS_GPART-LOW").text = ""
    session.findById("wnd[0]/usr/ctxtS_VKONT-LOW").text = ""

    # Insert spærtype
    session.findById("wnd[0]/usr/ctxtS_LOTYP-LOW").text = "51"

    # Insert spærreårsag by using clipboard
    session.findById("wnd[0]/usr/btn%_S_LOCKR_%_APP_%-VALU_PUSH").press()
    set_clipboard("\r\n".join("13689CDHIJKNUV"))
    session.findById("wnd[1]/tbar[0]/btn[24]").press()
    session.findById("wnd[1]/tbar[0]/btn[8]").press()

    # Search
    session.findById("wnd[0]/tbar[1]/btn[8]").press()

    # Save list as file
    file_path = os.path.join(os.getcwd(), "fplka.txt")
    export_file(session, file_path)
    fp_list, aftale_list = read_file(file_path)
    os.remove(file_path)

    return fp_list, aftale_list


def read_file(file_path) -> tuple[tuple[str]]:
    """Read a 'regneark' exported file from fplka.

    Args:
        file_path: The path to the file.

    Returns:
        A tuple of forretningspartnere and a tuple of aftaler.
    """
    fp_list = []
    aftale_list = []

    with open(file_path, encoding='cp1252') as file:
        for line in file:
            line = line.strip()

            if line.startswith("ForretnPartner"):
                fp = line.split("\t")[1]

            elif len(line) > 0 and line[0].isdigit():
                aftale = line.split("\t")[0]
                aftale = aftale.lstrip("0")
                aftale = aftale[:-12]

                fp_list.append(fp)
                aftale_list.append(aftale)

    return fp_list, aftale_list
