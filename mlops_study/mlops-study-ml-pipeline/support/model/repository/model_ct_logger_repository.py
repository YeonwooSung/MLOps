from support.infra.db import Db


class ModelCtLoggerRepository:
    MODEL_META_DB = Db()

    def __init__(self,
                 db: Db = MODEL_META_DB):
        self._db = db

    def logging_init(self, model_name: str, model_version: str):
        sql = f"""
            delete
              from mlops_meta.model_ct_log
             where model_name = '{model_name}'
               and model_version = '{model_version}'
            """
        self._db.execute(sql=sql)

    def logging_started(self,
                        model_name: str,
                        model_version: str,
                        cutoff_date: str):
        sql = f"""
            insert 
              into mlops_meta.model_ct_log 
                   (model_name, model_version, training_cutoff_date)
            values ('{model_name}', '{model_version}', 
                    '{cutoff_date}')
            """
        self._db.execute(sql=sql)

    def logging_finished(self,
                         model_name: str,
                         model_version: str,
                         metrics: str):
        sql = f"""
            update mlops_meta.model_ct_log
               set metrics = '{metrics}'
             where model_name = '{model_name}'
               and model_version = '{model_version}'
            """
        self._db.execute(sql=sql)

    def get_training_cutoff_date(self,
                                 model_name: str,
                                 model_version: str):
        sql = f"""
            select training_cutoff_date
              from mlops_meta.model_ct_log
             where model_name = '{model_name}'
               and model_version = '{model_version}'
            """
        training_cutoff_date = self._db.execute(sql=sql).fetchone()
        if training_cutoff_date:
            return training_cutoff_date[0]
        return None
