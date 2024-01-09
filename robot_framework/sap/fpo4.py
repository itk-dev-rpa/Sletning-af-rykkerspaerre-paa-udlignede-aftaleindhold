"""This module handles all actions relating to fpo4."""

import os

from robot_framework.sap.common import set_clipboard, export_file


def search_cases(session, fp_list: tuple[str], aftale_list: tuple[str]) -> set[tuple[str]]:
    """Search for open cases in SAP. Use the fp_list and aftale_list from
    fplka to filter to reduce the waiting time.

    Args:
        session: The SAP session object.
        fp_list: The list of FPs to filter on.
        aftale_list: The list of aftaler to filter on.

    Returns:
        set[tuple[str]]: A set of unique fp-aftale pairs (fp, aftale) for open cases.
    """
    session.startTransaction("fpo4")

    # Set fp filter
    session.findById("wnd[0]/usr/tabsTABSTRIP_TAB_B1/tabpTB11/ssub%_SUBSCREEN_TAB_B1:RFKKOP04:1001/btn%_S_GPART_%_APP_%-VALU_PUSH").press()
    set_clipboard("\r\n".join(fp_list))
    session.findById("wnd[1]/tbar[0]/btn[24]").press()
    session.findById("wnd[1]/tbar[0]/btn[8]").press()

    # Set aftale filter
    session.findById("wnd[0]/usr/tabsTABSTRIP_TAB_B1/tabpTB11/ssub%_SUBSCREEN_TAB_B1:RFKKOP04:1001/btn%_S_VTREF_%_APP_%-VALU_PUSH").press()
    set_clipboard("\r\n".join(aftale_list))
    session.findById("wnd[1]/tbar[0]/btn[24]").press()
    session.findById("wnd[1]/tbar[0]/btn[8]").press()

    # Set outputstyring
    session.findById("wnd[0]/usr/tabsTABSTRIP_TAB_B1/tabpTB12").select()
    session.findById("wnd[0]/usr/tabsTABSTRIP_TAB_B1/tabpTB12/ssub%_SUBSCREEN_TAB_B1:RFKKOP04:1002/ctxtP_NM_OPL").text = "STEPHAN"

    # Search
    session.findById("wnd[0]/tbar[1]/btn[8]").press()

    file_path = os.path.join(os.getcwd(), "fpo4.txt")
    export_file(session, file_path)
    fp_aftale_set = read_file(file_path)
    os.remove(file_path)

    return fp_aftale_set


def read_file(file_path: str) -> set[tuple[str]]:
    """Read the file from fpo4.
    For each line find the fp and aftale and add them to a set as
    a tuple to only return unique pairs.

    Args:
        file_path: The path to the file.

    Returns:
        set[tuple[str]]: A set of unique fp-aftale pairs (fp, aftale).
    """
    aftale_set = set()

    with open(file_path, encoding='cp1252') as file:
        # Skip first 3 lines
        for _ in range(3):
            file.readline()

        # Find header indexes
        headers = file.readline().split("\t")
        fp_index = headers.index("ForrPartn.")
        aftale_index = headers.index("Aftale")

        for line in file:
            if not line.strip():
                continue

            values = line.split("\t")
            fp = values[fp_index]
            aftale = values[aftale_index]
            aftale_set.add((fp, aftale))

    return aftale_set
