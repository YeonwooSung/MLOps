from typing import Union
from support.infra.db import Db


class ModelVersionRepository:
    MODEL_META_DB = Db()

    def __init__(self,
                 db: Db = MODEL_META_DB):
        self._db = db

    def get_final_ct_model_version(self, model_name: str) -> Union[str, None]:
        sql = f"""
            select concat_ws('.', a.major, a.minor, a.build) as final_ct_model_version
              from (select substring_index(model_version,'.', 1) as major
                          ,substring_index(substring_index(model_version, '.', 2),'.', -1) as minor
                          ,substring_index(model_version,'.', -1) as build
                      from mlops_meta.model_ct_log
                     where model_name = '{model_name}'
                   ) a
              order by cast(a.major as unsigned) desc
                      ,cast(a.minor as unsigned) desc
                      ,cast(a.build as unsigned) desc
             limit 1
            """
        final_ct_model_version = self._db.execute(sql=sql).fetchone()
        if final_ct_model_version:
            return final_ct_model_version[0]
        return None
