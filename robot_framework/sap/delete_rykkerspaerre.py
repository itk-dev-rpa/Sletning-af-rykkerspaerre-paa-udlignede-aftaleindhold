"""This module handles the deletion of rykkerspærrer."""

from itk_dev_shared_components.sap import tree_util
from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from OpenOrchestrator.database.queues import QueueStatus

from robot_framework import config


def delete_rykkerspaerre(session, orchestrator_connection: OrchestratorConnection, fp: str, aftale: str) -> None:
    """Delete the rykkerspærre on the given fp and aftale.
    This function assumes that the session already has fmcacov open.

    Args:
        session: _description_
        orchestrator_connection: _description_
        fp: _description_
        aftale: _description_
    """
    queue_element = orchestrator_connection.create_queue_element(config.QUEUE_NAME, f"{fp}:{aftale}")
    orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.IN_PROGRESS)

    # Sometimes the search turns up blank
    # Retry until it doesn't
    for _ in range(3):
        open_fp(session, fp, aftale)
        aftale_tree = session.findById("wnd[0]/shellcont/shell")
        try:
            # Check if the aftale is in the aftale tree
            node_key = tree_util.get_node_key_by_text(aftale_tree, aftale)
        except ValueError:
            continue

        break
    else:
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED, message="Aftalen kunne ikke findes.")
        raise RuntimeError("Search didn't turn up any result after 3 tries.")

    # Check postliste
    if not check_postliste(session):
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED, message="Postliste indeholdt rødt lyssignal.")
        return

    # Right click the aftale and select 'Ændr aftaleindhold'
    aftale_tree.nodeContextMenu(node_key)
    aftale_tree.selectContextMenuItemByText("Ændr aftaleindhold")

    # Go to 'Betalingsdata' and press 'Opret yderl. spærre'
    session.findById("wnd[0]/usr/subBDT_AREA:SAPLBUSS:0021/tabsBDT_TABSTRIP01/tabpBUSCR02_01").select()
    session.findById("wnd[0]/usr/subBDT_AREA:SAPLBUSS:0021/tabsBDT_TABSTRIP01/tabpBUSCR02_01/ssubGENSUB:SAPLBUSS:0029/ssubGENSUB:SAPLBUSS:7135/subA04P02:SAPLFMCA_PSOB_BDT2:0330/btnPUSH_DUNN_LOCK").press()

    # Mark all and delete
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[1]/tbar[0]/btn[25]").press()
    session.findById("wnd[1]/tbar[0]/btn[17]").press()

    # Save and return to fmcacov
    session.findById("wnd[0]/tbar[0]/btn[11]").press()
    session.findById("wnd[0]/tbar[0]/btn[3]").press()

    orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE)


def open_fp(session, fp: str, aftale: str):
    """Open the forretningspartner in fmcacov with a filter on the aftale.

    Args:
        session: The SAP session object.
        fp: The forretningspartner to open.
        aftale: The aftale to filter on.
    """
    session.findById("wnd[0]/usr/ctxtGPART_DYN").text = fp

    # Set aftale filter
    session.findById("wnd[0]/usr/btnZDKD_BP_FILTER").press()
    session.findById("wnd[1]/usr/tabsG_SELONETABSTRIP/tabpTAB001/ssubSUBSCR_PRESEL:SAPLSDH4:0220/sub:SAPLSDH4:0220/ctxtG_SELFLD_TAB-LOW[7,24]").text = aftale
    session.findById("wnd[1]/tbar[0]/btn[0]").press()

    # Select aftale in popup
    session.findById("wnd[1]/tbar[0]/btn[7]").press()
    session.findById("wnd[1]/tbar[0]/btn[0]").press()


def check_postliste(session) -> bool:
    """Check the postliste for any discrepancies.

    Args:
        session: The SAP session object.

    Returns:
        bool: True if the postliste is ok. False if the job should stop.
    """
    postliste_table = session.findById("wnd[0]/usr/tabsDATA_DISP/tabpDATA_DISP_FC1/ssubDATA_DISP_SCA:RFMCA_COV:0202/cntlRFMCA_COV_0100_CONT5/shellcont/shell")

    if postliste_table.rowCount == 0:
        return True

    # Check if any row has an entry with a red "Lyssignal"
    for index in range(postliste_table.rowCount):
        if postliste_table.getCellValue(index, "AMPEL") == r"@0A\QTilgodehavende åbent og forfaldent@":
            return False

    return True
