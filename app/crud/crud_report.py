from crud.base import CRUDBase
from models import Report
from schemas import ReportCreate, ReportUpdate


class CrudReport(CRUDBase[Report, ReportCreate, ReportUpdate]):
    pass


report = CrudReport(Report)
