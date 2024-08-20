import os
import unittest

os.environ['FEATURE_STORE_URL'] = f"mysql+pymysql://root:root@localhost/mlops"


class TestDb(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        from support.infra.db import Db
        cls.db = Db()

    def test_read_sql(self):
        sql = """select 1"""
        actual = self.db.read_sql(sql=sql)
        self.assertEqual([[1]], actual.values)

    def test_execute(self):
        sql = """drop table if exists temp.test_db"""
        self.db.execute(sql=sql)
        sql = """create table temp.test_db as select 1"""
        self.db.execute(sql=sql)
        sql = """insert into temp.test_db values (1)"""
        actual = self.db.execute(sql=sql)
        self.assertEqual(1, actual.rowcount)
        sql = """drop table temp.test_db"""
        self.db.execute(sql=sql)


if __name__ == '__main__':
    unittest.main()
