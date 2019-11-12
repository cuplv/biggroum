""" Deal with the residue for the musedev integration.

The residue is serialized and deserialized from json.

The residues saves the following information:
{
  "compilation_infos" : [compilation_info],
  "anomalies" : {}
}


compilation_info is
{
  cwd : Text,
  cmd : Text,
  args : [Text],
  classpath : [Text],
  files : [Text],
}

An anomaly is --- [TODO]

"""

class Residue:
    @staticmethod
    def append_compilation_info(residue, compilation_info):
        if residue is None: residue = {}
        if not "compilation_infos" in residue:
            residue["compilation_infos"] = []
        new_info = compilation_info
        residue["compilation_infos"].append(new_info)
        return residue

    @staticmethod
    def get_compilation_infos(residue):
        if residue is None:
            return []
        else:
            return residue["compilation_infos"]

    @staticmethod
    def get_files(compilation_info):
        return compilation_info["files"]

    @staticmethod
    def store_anomaly(residue, anomaly, note_id):
        if residue is None: residue = {}
        if not "anomalies" in residue: residue["anomalies"] = {}
        residue["anomalies"][note_id] = anomaly
        return residue

    @staticmethod
    def retrieve_anomaly(residue, note_id):
        if residue is None:
            return None
        elif not "anomalies" in residue:
            return None
        elif not note_id in residue["anomalies"]:
            return None
        else:
            return residue["anomalies"][note_id]

