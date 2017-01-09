""" Contains the db related code. """

import sqlalchemy as sql
try:
    from sqlalchemy.exceptions import OperationalError
except ImportError:
    from sqlalchemy.exc import OperationalError

import os
import logging

class IsoDb(object):
    def __init__(self, db_path):
        self.dburi = 'sqlite:///' + os.path.abspath(db_path)
        self.engine = sql.create_engine(self.dburi)
        self._open_db()

    def _open_db(self):
        try:
            self.engine.connect()
            self.engine.execute("SHOW DATABASES;")
            self.md = self._create_schema()
        except OperationalError:
            # Create the db
            self.engine = sql.create_engine(self.dburi)
            self.md = self._create_schema()
            # Create your missing database/tables/data her
            self.md.create_all(self.engine)

    def _create_schema(self):
        md = sql.MetaData()

        graphs = sql.Table(
            'graphs', md,
            sql.Column('id', sql.Integer, primary_key=True),
            sql.Column('methodname', sql.String(500), unique=True),
            sql.Column('relfilepath', sql.String(1000))
        )

        iso = sql.Table(
            'isos', md,
            sql.Column('id', sql.Integer, primary_key=True),
            sql.Column('idg1', None, sql.ForeignKey('graphs.id')),
            sql.Column('idg2', None, sql.ForeignKey('graphs.id')),
            sql.Column('relfilepath', sql.String(2000)),
            sql.Column('isoname', sql.String(1000)),
            sql.Column('weight', sql.Float)
        )

        logs = sql.Table(
            'logs', md,
            sql.Column('id', sql.Integer, primary_key=True),
            sql.Column('idiso', None, sql.ForeignKey('isos.id')),
            sql.Column('status', sql.String(20)),
            sql.Column('user_time', sql.Integer),
            sql.Column('iso_res', sql.String(6)))

        return md


    def add_graph(self, methodname, path):
        graphs = self.md.tables['graphs']
        res = self.engine.execute(graphs.insert(
            values={'methodname' : methodname,
                    'relfilepath' : path}))
        return res

    def get_graph_id(self, methodname):
        graphs = self.md.tables['graphs']
        res = self.engine.execute(graphs.select(
            graphs.c.methodname == methodname))
        return res.fetchone()[graphs.c.id]

    def add_iso(self, iso_list):
        isos = self.md.tables['isos']

        rec_list = []
        for (id1, id2, isoname, path, weight) in iso_list:
            rec_list.append({'idg1' : id1,
                             'idg2' : id2,
                             'relfilepath' : path,
                             'isoname' : isoname,
                             'weight' : weight})

        res = self.engine.execute(isos.insert(), rec_list)

        return res

    def get_iso_id(self, isoname):
        isos = self.md.tables['isos']
        res = self.engine.execute(isos.select(
            isos.c.isoname == isoname))
        return res.fetchone()[isos.c.id]

    def get_last_iso_id(self):
        isos = self.md.tables['isos']
        res = self.engine.execute("SELECT max(id) from isos")
        return res.fetchone()[0]

    def add_log(self, log_list):
        logs = self.md.tables['logs']

        rec_list = []
        i = 0
        count = 0

        # gest last id
        last_id = self.get_last_iso_id()
        assert(last_id >= len(log_list))
        current_id = last_id - len(log_list) + 1
        for (isoname, status, user_time, sys_time, iso_res) in log_list:
            try:
                weight = float(weight)
            except Exception as e:
                weight = 0
            try:
                user_time = float(user_time)
            except Exception as e:
                user_time = 0
            rec_list.append({'idiso' : current_id,
                             'status' : status,
                             'user_time' : user_time,
                             'iso_res' : iso_res})
            current_id = current_id + 1

        logging.info("Executing query...")
        res = self.engine.execute(logs.insert(),
                                  rec_list)
        return res


    def get_isos(self):
        sql = "select isos.isoname, isos.relfilepath, "\
              "g1.methodname, g2.methodname, " \
              "g1.relfilepath, g2.relfilepath, " \
              "weight from isos "\
              "join graphs g1 on g1.id = isos.idg1 " \
              "join graphs g2 on g2.id = isos.idg2"
        result = self.engine.execute(sql)
        return result

    def get_isos_by_weight(self, weight):
        sql = "select isos.isoname, isos.relfilepath, " \
              "g1.methodname, g2.methodname, " \
              "g1.relfilepath, g2.relfilepath, " \
              "weight from isos " \
              "join graphs g1 on g1.id = isos.idg1 " \
              "join graphs g2 on g2.id = isos.idg2 " \
              "where isos.weight >= %f" % weight
        logging.info("Retrieving data...")
        result = self.engine.execute(sql)
        return result

    def get_weight_stats(self):
        sql = "SELECT weight FROM isos"

        result = self.engine.execute(sql)
        number_list = []
        # check if we need incremental computation
        logging.info("Retrieving data...")
        for r in result:
            r = r[0]
            if r is None:
                logging.warning("Found none res")
            else:
                number_list.append(r)
        logging.info("Computing stats...")

        # print number_list
        try:
            import numpy
            average = numpy.average(number_list)
            stddev = numpy.std(number_list)
        except ImportError:
            logging.error("Cannot load numpy!")
            average = -1
            stddev = -1

        return (average, stddev)
