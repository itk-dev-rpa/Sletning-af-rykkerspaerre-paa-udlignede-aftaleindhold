"""This module contains common convenience functions."""

import os

import win32clipboard


def set_clipboard(text: str) -> None:
    """Private function to set text to the clipboard.

    Args:
        text: Text to set to clipboard.
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(text)
    win32clipboard.CloseClipboard()


def export_file(session, file_path: str):
    """Export a file as 'regneark'.

    Args:
        session: The SAP session object.
        file_path: The path to save the file at.
    """
    dir_path = os.path.dirname(file_path)
    file_name = os.path.basename(file_path)

    session.findById("wnd[0]/mbar/menu[0]/menu[1]/menu[2]").select()
    session.findById("wnd[1]/usr/subSUBSCREEN_STEPLOOP:SAPLSPO5:0150/sub:SAPLSPO5:0150/radSPOPLI-SELFLAG[1,0]").select()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
    session.findById("wnd[1]/usr/ctxtDY_PATH").text = dir_path
    session.findById("wnd[1]/usr/ctxtDY_FILENAME").text = file_name
    session.findById("wnd[1]/tbar[0]/btn[0]").press()
