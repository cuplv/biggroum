from protobuf3.fields import StringField, DoubleField, UInt64Field, MessageField
from protobuf3.message import Message


class Iso(Message):

    class MapNode(Message):
        pass

    class MapEdge(Message):
        pass

Iso.MapNode.add_field('id_1', UInt64Field(field_number=1, required=True))
Iso.MapNode.add_field('id_2', UInt64Field(field_number=2, required=True))
Iso.MapNode.add_field('weight', DoubleField(field_number=3, optional=True))
Iso.MapEdge.add_field('id_1', UInt64Field(field_number=1, required=True))
Iso.MapEdge.add_field('id_2', UInt64Field(field_number=2, required=True))
Iso.MapEdge.add_field('weight', DoubleField(field_number=3, optional=True))
Iso.add_field('graph_1_id', StringField(field_number=1, required=True))
Iso.add_field('graph_2_id', StringField(field_number=2, required=True))
Iso.add_field('map_node', MessageField(field_number=3, repeated=True, message_cls=Iso.MapNode))
Iso.add_field('map_edge', MessageField(field_number=4, repeated=True, message_cls=Iso.MapEdge))
Iso.add_field('weight', DoubleField(field_number=5, optional=True))
Iso.add_field('obj_value', DoubleField(field_number=6, optional=True))
Iso.add_field('dataNodeMatchCount', UInt64Field(field_number=7, optional=True))
Iso.add_field('dataEdgeMatchCount', UInt64Field(field_number=8, optional=True))
Iso.add_field('controlEdgeMatchCount', UInt64Field(field_number=9, optional=True))
Iso.add_field('methodNodeMatchCount', UInt64Field(field_number=10, optional=True))
Iso.add_field('averageMatchWeight', DoubleField(field_number=11, optional=True))
Iso.add_field('averageDataNodeInDegree', DoubleField(field_number=12, optional=True))
Iso.add_field('averageDataNodeOutDegree', DoubleField(field_number=13, optional=True))
Iso.add_field('averageMethodNodeInDegree', DoubleField(field_number=14, optional=True))
Iso.add_field('averageMethodNodeOutDegree', DoubleField(field_number=15, optional=True))
