import json
class Anomaly:
    @staticmethod
    def get_anomaly_list(json_input):
        anomaly_list = []
        for anomaly_json in json.loads(json_input):
            anomaly_list.append(Anomaly(anomaly_json))
        return anomaly_list

    def __init__(self, anomaly_json):
        """
        :param anomaly_json: json string of anomaly or parsed json string of anomaly
        """
        if isinstance(anomaly_json,str) or isinstance(anomaly_json,unicode):
            data = json.loads(anomaly_json)
        elif isinstance(anomaly_json,dict):
            data = anomaly_json
        else:
            raise Exception("Invalid anomaly input")

        self.parsed_json = data
        self.message = data["error"]
        self.file = data["fileName"]
        self.line = data["line"]
        self.column = 0 #TODO: no column provided
        self.function = data["methodName"]
        self.numeric_id = data["id"]

    def as_json(self):
        return json.dumps(self.parsed_json)

    def __eq__(self, other):
        # TODO: this is implemented for the unit test, is there a better way to avoid enumerating fields?
        return self.message == other.message \
               and self.file == other.file \
               and self.line == other.line \
               and self.column == other.column \
               and self.function == other.function \
               and self.numeric_id == other.numeric_id