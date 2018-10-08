"""
Store the features in a database
"""

import MySQLdb
import logging
from fixrgraph.stat_sig.feat import Feat


class FeatDb:
    DB_NAME = "groum_features"
    GRAPH_TABLE = "GRAPHS"
    FEATURE_TABLE = "FEATURES"
    FEAT_IN_GRAPHS_TABLE = "FEAT_IN_GRAPHS"
    PVALUES_TABLE = "PVALUES"

    def __init__(self, address, user, password, db_name = None):
        self.address = address
        self.user = user
        self.password = password
        self.db = None

        if db_name is None:
            self.db_name = FeatDb.DB_NAME
        else:
            self.db_name = db_name

    def _exec_sql(self, cursor, sql):
        logging.debug("SQL: %s" % sql)
        cursor.execute(sql)

    def _clean_db(self):
        cursor = self.db.cursor()
        sql = "DROP DATABASE IF EXISTS %s" % self.db_name
        self._exec_sql(cursor, sql)
        self.db.commit()

        cursor.close()

    def _init_db(self):
        self.db = MySQLdb.connect(host=self.address,
                                  user=self.user,
                                  passwd=self.password)

        # create db
        cursor = self.db.cursor()
        sql = "CREATE DATABASE IF NOT EXISTS %s" % self.db_name
        self._exec_sql(cursor, sql)

        self.db.select_db(self.db_name)

        self._exec_sql(cursor,
                       "CREATE DATABASE IF NOT EXISTS %s" % self.db_name)

        # create tables
        self._exec_sql(cursor,
                       "CREATE TABLE IF NOT EXISTS %s (" \
                       "id INT AUTO_INCREMENT," \
                       "description VARCHAR(500) NOT NULL,"
                       "PRIMARY KEY(id)," \
                       "CONSTRAINT tb_un UNIQUE (description)"\
                       ")" % FeatDb.GRAPH_TABLE)

        self._exec_sql(cursor,
                       "CREATE TABLE IF NOT EXISTS %s (" \
                       "id INT AUTO_INCREMENT," \
                       "description VARCHAR(500) NOT NULL,"
                       "PRIMARY KEY(id)," \
                       "CONSTRAINT tb_un UNIQUE (description)"\
                       ")" % FeatDb.FEATURE_TABLE)

        self.db.commit()

        self._exec_sql(cursor,
                       "CREATE TABLE IF NOT EXISTS %s (" \
                       "graph_id INT NOT NULL," \
                       "feat_id INT NOT NULL,"
                       "CONSTRAINT graph_key FOREIGN KEY(graph_id) references %s(id)," \
                       "CONSTRAINT feat_key FOREIGN KEY(feat_id) references %s(id)," \
                       "CONSTRAINT feat_unique PRIMARY KEY (graph_id,feat_id)" \
                       ")" % (FeatDb.FEAT_IN_GRAPHS_TABLE,
                              FeatDb.GRAPH_TABLE,
                              FeatDb.FEATURE_TABLE))
        self.db.commit()

        self._exec_sql(cursor,
                       "CREATE TABLE IF NOT EXISTS %s (" \
                       "graph_id INT NOT NULL," \
                       "pvalue DOUBLE, "
                       "CONSTRAINT pvalue_graph_key FOREIGN KEY(graph_id) references %s(id)," \
                       "CONSTRAINT pvalue_unique PRIMARY KEY (graph_id)" \
                       ")" % (FeatDb.PVALUES_TABLE,
                              FeatDb.GRAPH_TABLE))
        self.db.commit()

        cursor.close()


    def open(self):
        assert self.db is None
        self._init_db()

    def close(self):
        self.db.close()

    def insert_graph(self, graph_sig):
        cursor = self.db.cursor()

        sql = "INSERT IGNORE %s(description) VALUES('%s') " % (FeatDb.GRAPH_TABLE,
                                                               graph_sig)
        self._exec_sql(cursor, sql)
        self.db.commit()
        cursor.close()


    def insert_feat(self, graph_name, feat):
        cursor = self.db.cursor()

        # Insert the feature
        sql = "INSERT IGNORE %s(description) VALUES('%s')" % (FeatDb.FEATURE_TABLE,
                                                              feat.desc)
        self._exec_sql(cursor, sql)

        # Insert the feature
        sql = "INSERT IGNORE INTO %s (graph_id,feat_id) " \
              "SELECT %s.id, %s.id " \
              "FROM %s, %s " \
              "WHERE %s.description = '%s' AND " \
              "%s.description = '%s'" % (FeatDb.FEAT_IN_GRAPHS_TABLE,
                                         FeatDb.GRAPH_TABLE,
                                         FeatDb.FEATURE_TABLE,
                                         FeatDb.GRAPH_TABLE,
                                         FeatDb.FEATURE_TABLE,
                                         FeatDb.GRAPH_TABLE,
                                         graph_name,
                                         FeatDb.FEATURE_TABLE,
                                         feat.desc)
        self._exec_sql(cursor, sql)
        self.db.commit()
        cursor.close()

    def insert_pval(self, graph_name, pvalue):
        cursor = self.db.cursor()

        # Insert the feature
        sql = "INSERT IGNORE INTO %s (graph_id,pvalue) " \
              "SELECT %s.id, %f " \
              "FROM %s " \
              "WHERE %s.description = '%s'" \
              "" % (FeatDb.PVALUES_TABLE,
                    FeatDb.GRAPH_TABLE,
                    pvalue,
                    FeatDb.GRAPH_TABLE,
                    FeatDb.GRAPH_TABLE,
                    graph_name)

        self._exec_sql(cursor, sql)

        self.db.commit()
        cursor.close()



    def count_features(self, feature_list):
        # Count the number of graphs that contains all the
        # features in feature_list

        if (len(feature_list) == 0):
            return 0

        feat_sql = None
        for feat in feature_list:
            if (feat_sql is None):
                feat_sql = "SELECT DISTINCT %s.graph_id FROM %s " \
                  "INNER JOIN FEATURES ON %s.feat_id = %s.id " \
                  "WHERE %s.description = '%s'" % (FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                   FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                   FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                   FeatDb.FEATURE_TABLE,
                                                   FeatDb.FEATURE_TABLE,
                                                   feat.desc)

            else:
                feat_sql = "SELECT DISTINCT %s.graph_id FROM %s " \
                  "INNER JOIN FEATURES ON %s.feat_id = %s.id " \
                  "WHERE %s.description = '%s' AND " \
                  "%s.graph_id IN (%s)" \
                  "" % (FeatDb.FEAT_IN_GRAPHS_TABLE,
                        FeatDb.FEAT_IN_GRAPHS_TABLE,
                        FeatDb.FEAT_IN_GRAPHS_TABLE,
                        FeatDb.FEATURE_TABLE,
                        FeatDb.FEATURE_TABLE,
                        feat.desc,
                        FeatDb.FEAT_IN_GRAPHS_TABLE,
                        feat_sql)

        sql = "SELECT COUNT(DISTINCT(%s.graph_id)) FROM %s WHERE " \
              "%s.graph_id IN (%s)" % (FeatDb.FEAT_IN_GRAPHS_TABLE,
                                       FeatDb.FEAT_IN_GRAPHS_TABLE,
                                       FeatDb.FEAT_IN_GRAPHS_TABLE,
                                       feat_sql)

        cursor = self.db.cursor()
        self._exec_sql(cursor, sql)
        count = cursor.fetchone()

        cursor.close()
        return count[0]

    def count_all_graphs(self):
        # Count the number of the graphs
        cursor = self.db.cursor()
        sql = "SELECT COUNT(*) FROM %s" % (FeatDb.GRAPH_TABLE)
        self._exec_sql(cursor, sql)
        count = cursor.fetchone()
        cursor.close()

        return count


