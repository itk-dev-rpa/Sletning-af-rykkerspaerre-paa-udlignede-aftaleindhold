"""This module contains the main process of the robot."""

from OpenOrchestrator.orchestrator_connection.connection import OrchestratorConnection
from itk_dev_shared_components.sap import multi_session

from robot_framework.sap import fplka, fpo4, delete_rykkerspaerre


def process(orchestrator_connection: OrchestratorConnection) -> None:
    """Do the primary process of the robot."""
    orchestrator_connection.log_trace("Running process.")

    session = multi_session.spawn_sessions(1)[0]

    # Search all rykkerspærre
    fp_list, aftale_list = fplka.search_cases(session)

    # Return to start screen
    session.findById("wnd[0]/tbar[0]/btn[12]").press()
    session.findById("wnd[0]/tbar[0]/btn[12]").press()

    # Search all open cases
    fpo4_cases = fpo4.search_cases(session, fp_list, aftale_list)

    # Return to start screen
    session.findById("wnd[0]/tbar[0]/btn[12]").press()
    session.findById("wnd[0]/tbar[0]/btn[12]").press()

    # Filter away all open cases from rykkerspærre list
    fplka_cases = set(zip(fp_list, aftale_list))
    work_list = list(fplka_cases - fpo4_cases)

    session.startTransaction("fmcacov")
    for case in work_list:
        delete_rykkerspaerre.delete_rykkerspaerre(session, orchestrator_connection, case[0], case[1])


if __name__ == '__main__':
    import os
    conn_string = os.getenv("OpenOrchestratorConnString")
    crypto_key = os.getenv("OpenOrchestratorKey")
    oc = OrchestratorConnection("Sletning Test", conn_string, crypto_key, "")
    process(oc)
