"""This module handles the deletion of rykkerspærrer."""

from itk_dev_shared_components.sap import tree_util, fmcacov
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

    fmcacov.open_forretningspartner(session, fp)
    aftale_tree = session.findById("wnd[0]/shellcont/shell")
    try:
        # Check if the aftale is in the aftale tree
        node_key = tree_util.get_node_key_by_text(aftale_tree, aftale)
    except ValueError:
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED, message="Aftalen kunne ikke findes.")
        return

    # Check postliste
    if not check_postliste(session):
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.FAILED, message="Postliste indeholdt rødt lyssignal.")
        return

    # Right click the aftale and select 'Ændr aftaleindhold'
    aftale_tree.nodeContextMenu(node_key)
    aftale_tree.selectContextMenuItemByText("Ændr aftaleindhold")

    # Go to 'Betalingsdata'
    session.findById("wnd[0]/usr/subBDT_AREA:SAPLBUSS:0021/tabsBDT_TABSTRIP01/tabpBUSCR02_01").select()

    # Check if rykkerspærre should be skipped
    rs_type = session.findById("wnd[0]/usr/subBDT_AREA:SAPLBUSS:0021/tabsBDT_TABSTRIP01/tabpBUSCR02_01/ssubGENSUB:SAPLBUSS:0029/ssubGENSUB:SAPLBUSS:7135/subA04P02:SAPLFMCA_PSOB_BDT2:0330/ctxtSPSOB_SCR_2110_H3-DUNN_REASON").text
    rs_date = session.findById("wnd[0]/usr/subBDT_AREA:SAPLBUSS:0021/tabsBDT_TABSTRIP01/tabpBUSCR02_01/ssubGENSUB:SAPLBUSS:0029/ssubGENSUB:SAPLBUSS:7135/subA04P03:SAPLZDKD0001_CUSTOM_SCREENS:0510/ctxtGV_DUNN_TDATE_CO").text

    if (rs_type == 'H' and rs_date == '31.12.2999'):
        # Skip and go back
        session.findById("wnd[0]/tbar[0]/btn[3]").press()
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE, message="Sprunget over: H 31.12.2999")
        return

    if rs_type == 'I':
        # Skip and go back
        session.findById("wnd[0]/tbar[0]/btn[3]").press()
        orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE, message="Sprunget over: I")
        return

    # Press 'Opret yderl. spærre'
    session.findById("wnd[0]/usr/subBDT_AREA:SAPLBUSS:0021/tabsBDT_TABSTRIP01/tabpBUSCR02_01/ssubGENSUB:SAPLBUSS:0029/ssubGENSUB:SAPLBUSS:7135/subA04P02:SAPLFMCA_PSOB_BDT2:0330/btnPUSH_DUNN_LOCK").press()

    # Mark all and delete
    session.findById("wnd[1]/tbar[0]/btn[8]").press()
    session.findById("wnd[1]/tbar[0]/btn[25]").press()
    session.findById("wnd[1]/tbar[0]/btn[17]").press()

    # Save and return to fmcacov
    session.findById("wnd[0]/tbar[0]/btn[11]").press()
    session.findById("wnd[0]/tbar[0]/btn[3]").press()

    orchestrator_connection.set_queue_element_status(queue_element.id, QueueStatus.DONE)


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
