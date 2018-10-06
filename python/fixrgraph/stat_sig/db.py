"""
Store the features in a database
"""

import MySQLdb
from fixrgraph.stat_sig.feat import Feat


class FeatDb:

    DB_NAME = "groum_features"
    GRAPH_TABLE = "GRAPHS"
    FEATURE_TABLE = "FEATURES"
    FEAT_IN_GRAPHS_TABLE = "FEAT_IN_GRAPHS"

    def __init__(self, address, user, password):
        self.address = address
        self.user = user
        self.password = password
        self.db = None


    def _init_db(self):
        self.db = MySQLdb.connect(host=address, user=user,passwd=password)

        # create db
        cursor = self.db.cursor()
        sql = "CREATE DATABASE IF NOT EXISTS %s" % FeatDb.DB_NAME
        cursor.execute(sql)

        self.db.select_db(FeatDb.DB_NAME)

        # create tables
        cursor.execute("CREATE TABLE IF NOT EXISTS %s (" \
                       "id INT AUTO_INCREMENT," \
                       "desc TEXT NOT NULL,"
                       "PRIMARY_KEY(id)," \
                       "CONSTRAINT tb_un UNIQUE (desc)"\
                       ")" % FeatDb.GRAPH_TABLE)

        cursor.execute("CREATE TABLE IF NOT EXISTS %s (" \
                       "id INT AUTO_INCREMENT," \
                       "desc TEXT NOT NULL,"
                       "PRIMARY_KEY(id)," \
                       "CONSTRAINT tb_un UNIQUE (desc)"\
                       ")" % FeatDb.FEATURE_TABLE)

        cursor.execute("CREATE TABLE IF NOT EXISTS %s (" \
                       "graph_id INT NOT NULL," \
                       "feat_id TEXT NOT NULL,"
                       "CONSTRAINT graph_key FOREIGN KEY(graph_id)," \
                       "CONSTRAINT feat_key FOREIGN KEY(feat_id)," \
                       "CONSTRAINT feat_unique PRIMARY KEY (graph_id,feat_id)," \
                       ")" % FeatDb.FEAT_IN_GRAPHS)
        cursor.close()


    def open(self):
        assert not self.db.open()
        self._init_db()

    def close(self):
        assert self.db.open()
        self.db.close()

    def insert_feat(self, graph_name, feat):
        assert self.db.open()
        cursor = self.db.cursor()

        # Insert the feature
        sql = "INSERT IGNORE %s(x) VALUES(%s)" % (FeatDb.FEATURE_TABLE,
                                                  feat.desc)
        cursor.execute()

        # Insert the feature
        sql = "INSERT IGNORE INTO %s (x,y)" \
              "VALUES(SELECT id FROM %s WHERE desc = %s," \
              "SELECT id from %s WHERE desc = %s)" % (FeatDb.FEAT_IN_GRAPHS,
                                                      FeatDb.GRAPH_TABLE,
                                                      graph_name,
                                                      FeatDb.FEATURE_TABLE,
                                                      feat.desc)
        cursor.execute()
        cursor.close()

    def insert_graph(self, graph_sig):
        assert self.db.open()
        cursor = self.db.cursor()

        sql = "INSERT IGNORE %s(x) VALUES(%s) " % (FeatDb.GRAPH_TABLE,
                                                   graph_sig)


        cursor.execute()
        cursor.close()

    def count_features(self):
        assert self.db.open()

        raise NotImplementedError


