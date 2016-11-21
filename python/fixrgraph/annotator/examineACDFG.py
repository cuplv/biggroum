#! /usr/bin/python

from __future__ import print_function
import sys
#import proto_acdfg_pb2
import protobuf.proto_acdfg_pb2

def examineRepoTag(rTag):
    print('Repo Information:')
    if (rTag.HasField('repo_name')):
        print('\t RepoName=',rTag.repo_name)
    if (rTag.HasField('user_name')):
        print('\t UserName=',rTag.user_name)
    if (rTag.HasField('url')):
        print('\t URL=',rTag.url)
    if (rTag.HasField('commit_hash')):
        print('\t Commit Hash=',rTag.commit_hash)

def examineSourceInfo(sInfo):
    fields=['package_name','class_name','method_name','class_line_number','method_line_number','source_class_name','abs_source_class_name']
    print('Source Information:')
    for val in fields:
        if (sInfo.HasField(val)):
            print(val,'=',getattr(sInfo,val))

def examineDataNode(dNode):
    print('Data Node # ',dNode.id, dNode.name,':', dNode.type)

def examineMethodNode(dNode):
    print('Method Node #', dNode.id, end=' ')
    if (dNode.HasField('invokee')):
        print(dNode.invokee,'->',end='')
    print( dNode.name, end='')
    print('(',end='')
    sep=''
    for id in dNode.argument:
        print(id,sep,end='')
        sep=','
    print(')')

def examineEdge(typ, edg):
    print(typ,' edge #',edg.id,':',getattr(edg,'from'),'->',edg.to)

def examine(acdfg):
    if (acdfg.HasField('repo_tag')):
        rTag=acdfg.repo_tag
        examineRepoTag(rTag)
    if (acdfg.HasField('source_info')):
        examineSourceInfo(acdfg.source_info)

    for dNode in acdfg.data_node:
        examineDataNode(dNode)
    for mNode in acdfg.method_node:
        examineMethodNode(mNode)

    for dEdge in acdfg.def_edge:
        examineEdge('DefEdge ',dEdge)

    for uEdge in acdfg.use_edge:
        examineEdge('UseEdge ',uEdge)

    for cEdge in acdfg.control_edge:
        examineEdge('CtrlEdge ',cEdge)

    for tEdge in acdfg.trans_edge:
        examineEdge('TransitiveEdge',tEdge)


def main(argv):
    if (len(argv) < 2):
        print('Usage: examineACDFG.py <name of what to examine> ')
        sys.exit(1)
    f=open(sys.argv[1],'rb')
    acdfg=proto_acdfg_pb2.Acdfg() # create a new acdfg
    acdfg.ParseFromString(f.read())
    f.close()

    examine(acdfg)



main(sys.argv)
