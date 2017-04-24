import logging

class MissingProtobufField(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def upload_pool(solr, threshold, doc_pool):
    if (len(doc_pool) >= threshold or threshold < 0):
        logging.info("Uploading %d documents to Solr..." % len(doc_pool))
        solr.add(doc_pool)
        doc_pool = []
    return doc_pool

