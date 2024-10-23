from crud.base import CRUDBase
from models import Data
from schemas import DataCreate, DataUpdate


class CrudData(CRUDBase[Data, DataCreate, DataUpdate]):

    pass


data = CrudData(Data)
