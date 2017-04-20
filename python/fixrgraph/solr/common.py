class MissingProtobufField(Exception):
    def __init__(self, value):
        self.parameter = value
    def __str__(self):
        return repr(self.parameter)

def upload_pool(solr, threshold, doc_pool):
    if (len(doc_pool) >= threshold):
        logging.info("Uploading solr docs...")
        solr.add(doc_pool)
        doc_pool = []
    return doc_pool

