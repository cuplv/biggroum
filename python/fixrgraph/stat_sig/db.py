"""
Store the features in a database
"""

import logging
from fixrgraph.stat_sig.feat import Feat


class FeatDb:
    DB_NAME = "groum_features"
    GRAPH_TABLE = "GRAPHS"
    FEATURE_TABLE = "FEATURES"
    FEAT_IN_GRAPHS_TABLE = "FEAT_IN_GRAPHS"
    PVALUES_TABLE = "PVALUES"
    VIEW_METHODS = "METHODS"
    VIEW_EDGES = "EDGES"

    @staticmethod
    def get_result_set(cursor):
        res = set()
        for elem in cursor:
            res.add(elem[0])
        return res


    def __init__(self, address, user, password, db_name = None):
        self.address = address
        self.user = user
        self.password = password
        self.db = None

        if db_name is None:
            self.db_name = FeatDb.DB_NAME
        else:
            self.db_name = db_name

        self.graph_count = None
        self.memo = {}

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
        print self.address
        print self.user
        print self.password

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


        query = "CREATE VIEW %s AS " \
                "SELECT graph_id, feat_id FROM %s " \
                "INNER JOIN %s " \
                "ON %s.feat_id = %s.id " \
                "WHERE %s.description LIKE '%% -> %%'" % (FeatDb.VIEW_EDGES,
                                                          FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                          FeatDb.FEATURE_TABLE,
                                                          FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                          FeatDb.FEATURE_TABLE,
                                                          FeatDb.FEATURE_TABLE)
#        self._exec_sql(cursor, query)
#        self.db.commit()

        query = "CREATE VIEW %s AS " \
                "SELECT graph_id, feat_id FROM %s " \
                "INNER JOIN %s " \
                "ON %s.feat_id = %s.id " \
                "WHERE NOT %s.description LIKE '%% -> %%'" % (FeatDb.VIEW_METHODS,
                                                              FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                              FeatDb.FEATURE_TABLE,
                                                              FeatDb.FEAT_IN_GRAPHS_TABLE,
                                                              FeatDb.FEATURE_TABLE,
                                                              FeatDb.FEATURE_TABLE)
#        self._exec_sql(cursor, query)
#        self.db.commit()


        cursor.close()


    def open(self):
        assert self.db is None
        self._init_db()

    def close(self):
        self.db.close()

    def insert_features(self, graph_sig, features):
        cursor = self.db.cursor()

        self._insert_graph(graph_sig, cursor)

        print "inserting..."
        for feat in features:
            print feat
            self._insert_feat(graph_sig, feat, cursor)

        self.db.commit()
        cursor.close()


    def _insert_graph(self, graph_sig, cursor):
        sql = "INSERT IGNORE %s(description) VALUES('%s') " % (FeatDb.GRAPH_TABLE,
                                                               graph_sig)
        self._exec_sql(cursor, sql)


    def _insert_feat(self, graph_name, feat, cursor):
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


    def get_graphs_for_methods(self, method_list):
        feat_sql = None

        graphs_with_other_feat = "SELECT DISTINCT %s.graph_id FROM %s " \
                                 "INNER JOIN %s ON %s.feat_id = %s.id " \
                                 "WHERE TRUE " % (FeatDb.VIEW_METHODS,
                                                  FeatDb.VIEW_METHODS,
                                                  FeatDb.FEATURE_TABLE,
                                                  FeatDb.VIEW_METHODS,
                                                  FeatDb.FEATURE_TABLE)

        for feat in method_list:
            app = "SELECT DISTINCT %s.graph_id FROM %s " \
              "INNER JOIN %s ON %s.feat_id = %s.id " \
              "WHERE %s.description = '%s'" % (FeatDb.VIEW_METHODS,
                                               FeatDb.VIEW_METHODS,
                                               FeatDb.FEATURE_TABLE,
                                               FeatDb.VIEW_METHODS,
                                               FeatDb.FEATURE_TABLE,
                                               FeatDb.FEATURE_TABLE,
                                               feat.desc)

            if (feat_sql is None):
                feat_sql = app
            else:
                feat_sql = "%s AND %s.graph_id IN (%s)" % (app,
                                                           FeatDb.VIEW_METHODS,
                                                           feat_sql)


            graphs_with_other_feat = "%s AND %s.description != '%s'" % (graphs_with_other_feat,
                                                                        FeatDb.FEATURE_TABLE,
                                                                        feat.desc)

        sql = "SELECT DISTINCT %s.graph_id FROM %s WHERE " \
              "%s.graph_id IN (%s) AND " \
              "%s.graph_id NOT IN (%s) " % (FeatDb.VIEW_METHODS,
                                            FeatDb.VIEW_METHODS,
                                            FeatDb.VIEW_METHODS,
                                            feat_sql,
                                            FeatDb.VIEW_METHODS,
                                            graphs_with_other_feat)

        cursor = self.db.cursor()
        self._exec_sql(cursor, sql)

        res = FeatDb.get_result_set(cursor)
        cursor.close()

        return res


    def get_graphs_for_edge(self, edge, neg=False):
        key = (edge.desc, neg)

        if key in self.memo:
            return self.memo[key]

        feat_sql = "SELECT DISTINCT %s.graph_id FROM %s " \
              "INNER JOIN %s ON %s.feat_id = %s.id " \
              "WHERE %s.description ='%s'" % (FeatDb.VIEW_EDGES,
                                              FeatDb.VIEW_EDGES,
                                              FeatDb.FEATURE_TABLE,
                                              FeatDb.VIEW_EDGES,
                                              FeatDb.FEATURE_TABLE,
                                              FeatDb.FEATURE_TABLE,
                                              edge.desc)

        if (neg):
            # complement
            feat_sql = "SELECT DISTINCT %s.graph_id FROM %s " \
                       "WHERE %s.graph_id NOT IN (%s)"  % (FeatDb.VIEW_EDGES,
                                                           FeatDb.VIEW_EDGES,
                                                           FeatDb.VIEW_EDGES,
                                                           feat_sql)


        cursor = self.db.cursor()
        self._exec_sql(cursor, feat_sql)

        res = FeatDb.get_result_set(cursor)
        cursor.close()

        self.memo[key] = res

        return res

    def get_graphs_for_edge_id(self, edge_id, neg=False):
        key = (edge_id, neg)
        if key in self.memo:
            return self.memo[key]

        feat_sql = "SELECT DISTINCT %s.graph_id FROM %s " \
                   "WHERE %s.feat_id = %s " % (FeatDb.VIEW_EDGES,
                                               FeatDb.VIEW_EDGES,
                                               edge_id)

        if (neg):
            # complement
            feat_sql = "SELECT DISTINT %s.graph_id FROM %s " \
                       "WHERE %s.graph_id NOT IN (%s)"  % (FeatDb.VIEW_EDGES,
                                                           FeatDb.VIEW_EDGES,
                                                           feat_sql)



        cursor = self.db.cursor()
        self._exec_sql(cursor, feat_sql)

        res = FeatDb.get_result_set(cursor)
        cursor.close()

        self.memo[key] = res

        return res


    def get_not_included_edges(self, methodEdges, methodCalls):
        cm_a= "FALSE"
        cm_b= "FALSE"
        for m in methodCalls:
            cm_a = '%s OR a.description = "%s"' % (cm_a, m.desc)
            cm_b = '%s OR b.description = "%s"' % (cm_b, m.desc)

        condition_edges = "TRUE"
        for e in methodEdges:
            condition_edges = "%s AND f.description != '%s' " % (condition_edges, e.desc)

        condition = "(%s) AND (%s) AND (%s)" % (cm_a, cm_b, condition_edges)

        select = "SELECT f.id, a.description, b.description "\
                 "FROM FEATURES a, FEATURES b, FEATURES f " \
                 " WHERE " \
                 " %s " \
                 " AND " \
                 " a.id IN (SELECT feat_id FROM METHODS) " \
                 " AND " \
                 " b.id IN (SELECT feat_id FROM METHODS) " \
                 " AND " \
                 " f.id IN (SELECT feat_id FROM EDGES) " \
                 " AND " \
                 ' f.description =  CONCAT(CONCAT(a.description, " -> "), b.description) ' % condition

        cursor = self.db.cursor()
        self._exec_sql(cursor, select)
        res = FeatDb.get_result_set(cursor)
        cursor.close()

        return res


    def count_all_graphs(self):
        # Count the number of the graphs
        if self.graph_count is None:
            cursor = self.db.cursor()
            sql = "SELECT COUNT(*) FROM %s" % (FeatDb.GRAPH_TABLE)

            self._exec_sql(cursor, sql)
            count = cursor.fetchone()
            cursor.close()

            self.graph_count = count[0]

        return self.graph_count


