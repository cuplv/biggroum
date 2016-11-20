from enum import Enum
from protobuf3.message import Message
from protobuf3.fields import StringField, EnumField, UInt32Field, MessageField, UInt64Field


class Acdfg(Message):

    class EdgeLabel(Enum):
        DOMINATE = 0
        POSTDOMINATED = 1

    class DataNode(Message):

        class DataType(Enum):
            DATA_VAR = 0
            DATA_CONST = 1

    class MiscNode(Message):
        pass

    class MethodNode(Message):
        pass

    class ControlEdge(Message):
        pass

    class DefEdge(Message):
        pass

    class UseEdge(Message):
        pass

    class TransEdge(Message):
        pass

    class ExceptionalControlEdge(Message):
        pass

    class LabelMap(Message):
        pass

    class RepoTag(Message):
        pass

    class MethodBag(Message):
        pass

    class SourceInfo(Message):
        pass

Acdfg.DataNode.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.DataNode.add_field('name', StringField(field_number=2, required=True))
Acdfg.DataNode.add_field('type', StringField(field_number=3, required=True))
Acdfg.DataNode.add_field('data_type', EnumField(field_number=4, optional=True, enum_cls=Acdfg.DataNode.DataType))
Acdfg.MiscNode.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.MethodNode.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.MethodNode.add_field('assignee', UInt64Field(field_number=5, optional=True))
Acdfg.MethodNode.add_field('invokee', UInt64Field(field_number=2, optional=True))
Acdfg.MethodNode.add_field('name', StringField(field_number=3, required=True))
Acdfg.MethodNode.add_field('argument', UInt64Field(field_number=4, repeated=True))
Acdfg.ControlEdge.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.ControlEdge.add_field('from', UInt64Field(field_number=2, required=True))
Acdfg.ControlEdge.add_field('to', UInt64Field(field_number=3, required=True))
Acdfg.DefEdge.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.DefEdge.add_field('from', UInt64Field(field_number=2, required=True))
Acdfg.DefEdge.add_field('to', UInt64Field(field_number=3, required=True))
Acdfg.UseEdge.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.UseEdge.add_field('from', UInt64Field(field_number=2, required=True))
Acdfg.UseEdge.add_field('to', UInt64Field(field_number=3, required=True))
Acdfg.TransEdge.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.TransEdge.add_field('from', UInt64Field(field_number=2, required=True))
Acdfg.TransEdge.add_field('to', UInt64Field(field_number=3, required=True))
Acdfg.ExceptionalControlEdge.add_field('id', UInt64Field(field_number=1, required=True))
Acdfg.ExceptionalControlEdge.add_field('from', UInt64Field(field_number=2, required=True))
Acdfg.ExceptionalControlEdge.add_field('to', UInt64Field(field_number=3, required=True))
Acdfg.ExceptionalControlEdge.add_field('exceptions', StringField(field_number=4, repeated=True))
Acdfg.LabelMap.add_field('edge_id', UInt64Field(field_number=1, required=True))
Acdfg.LabelMap.add_field('labels', EnumField(field_number=2, repeated=True, enum_cls=Acdfg.EdgeLabel))
Acdfg.RepoTag.add_field('repo_name', StringField(field_number=1, optional=True))
Acdfg.RepoTag.add_field('user_name', StringField(field_number=2, optional=True))
Acdfg.RepoTag.add_field('url', StringField(field_number=3, optional=True))
Acdfg.RepoTag.add_field('commit_hash', StringField(field_number=4, optional=True))
Acdfg.MethodBag.add_field('method', StringField(field_number=1, repeated=True))
Acdfg.SourceInfo.add_field('package_name', StringField(field_number=1, optional=True))
Acdfg.SourceInfo.add_field('class_name', StringField(field_number=2, optional=True))
Acdfg.SourceInfo.add_field('method_name', StringField(field_number=3, optional=True))
Acdfg.SourceInfo.add_field('class_line_number', UInt32Field(field_number=4, optional=True))
Acdfg.SourceInfo.add_field('method_line_number', UInt32Field(field_number=5, optional=True))
Acdfg.SourceInfo.add_field('source_class_name', StringField(field_number=6, optional=True))
Acdfg.SourceInfo.add_field('abs_source_class_name', StringField(field_number=7, optional=True))
Acdfg.add_field('data_node', MessageField(field_number=1, repeated=True, message_cls=Acdfg.DataNode))
Acdfg.add_field('misc_node', MessageField(field_number=2, repeated=True, message_cls=Acdfg.MiscNode))
Acdfg.add_field('method_node', MessageField(field_number=3, repeated=True, message_cls=Acdfg.MethodNode))
Acdfg.add_field('control_edge', MessageField(field_number=4, repeated=True, message_cls=Acdfg.ControlEdge))
Acdfg.add_field('def_edge', MessageField(field_number=5, repeated=True, message_cls=Acdfg.DefEdge))
Acdfg.add_field('use_edge', MessageField(field_number=6, repeated=True, message_cls=Acdfg.UseEdge))
Acdfg.add_field('trans_edge', MessageField(field_number=7, repeated=True, message_cls=Acdfg.TransEdge))
Acdfg.add_field('exceptional_edge', MessageField(field_number=12, repeated=True, message_cls=Acdfg.ExceptionalControlEdge))
Acdfg.add_field('edge_labels', MessageField(field_number=11, repeated=True, message_cls=Acdfg.LabelMap))
Acdfg.add_field('repo_tag', MessageField(field_number=8, optional=True, message_cls=Acdfg.RepoTag))
Acdfg.add_field('source_info', MessageField(field_number=10, optional=True, message_cls=Acdfg.SourceInfo))
Acdfg.add_field('method_bag', MessageField(field_number=9, optional=True, message_cls=Acdfg.MethodBag))
