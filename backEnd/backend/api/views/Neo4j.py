from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view, permission_classes
from django.http import JsonResponse
from ..models.file import file
from ..models.concEle import Concele
from itertools import combinations
from ..models.suggestConc import SuggestConc
from ..models.gConc import GConc
from ..utils.suggest import get_unseen_pairs
from ..utils.synonyms import synonyms
from ..models.concEle import Concele
from ..models.gRel import gRel
from ..models.component import component
import pandas as pd
from ..serializers.suggestConcSerializer import SuggestConc
from ..utils.Neo4jSp import create_node, update_node_by_id, create_relationship,run_query, remove_descendants_from_relationships,remove_descendants,update_relationship, overload
from ..utils.neo4j_driver import driver, close_driver
from ..permissions.permission import IsSuperAdmin
from ..utils.Wraps import before_and_after_view
from ..permissions.permission import IsAdmin

@permission_classes([IsAdmin])  
@api_view(['POST'])
def dele_graph(request):
    data=request.data
    id = data.get('idlaw')
    lstid = component.objects.filter(idLaw = id).values_list('id')
    remove_descendants_from_relationships(lstid)
    remove_descendants(lstid)
def node():
    try:
        lstNode = GConc.objects.filter(updateNeo4j = 1)
        for item in lstNode:
            prop = {'node_id' : item.id ,'lstConC': list(dict.fromkeys(item.lstConC)), 'meaning': item.meaning,'descendants': list(dict.fromkeys(item.descendants))}
            create_node(driver=driver, properties=prop)
            print(node)
            item.updateNeo4j = 0
            item.save()
        
        lstNode = GConc.objects.filter(updateNeo4j = 2)
        for item in lstNode:
            prop = {'lstConC': item.lstConC, 'meaning': item.meaning,'descendants': item.descendants}
            update_node_by_id(driver=driver, node_id=item.id , updates=prop)
            item.updateNeo4j = 0
            item.save()
        return True
        
    except Exception as e:
        print("conc", e)
        return False
    
def relation():
    try:
        lstrel = gRel.objects.exclude(Q(update_concs=None)| Q(update_concs=[]))
        
        for item in lstrel:
            prop = {'relation_id' : item.id,'lstRel':  list(dict.fromkeys(item.lstRel)), 'meaning': item.meaning,'descendants': list(dict.fromkeys(item.descendants)) }
            for count in range(len(item.update_conco)):
                print("4")

                create_relationship(driver=driver,start_node_id=item.update_concs[count], end_node_id=item.update_conco[count],rel_properties=prop)
            item.update_conco = []
            item.update_concs = []
            item.save()
        lstrel = gRel.objects.filter(updaterel = 1)
        for item in lstrel:
            for count in range(len(item.update_conco)):
                prop = {'relation_id' : item.id,'lstRel': item.lstRel, 'meaning': item.meaning,'descendants': item.descendants}
                update_relationship(driver=driver,rel_id=item.id,rel_properties=prop)
            item.update_conco = []
            item.update_concs = []
            item.updaterel=0
            item.save()
        return True
    except Exception as e:
        print("relation")
        print(e)
        return False
    
@permission_classes([IsAdmin])  
@api_view(['POST'])
@before_and_after_view(number=2)
def init_graph_data(request):
    if overload() and node() and relation():
        return JsonResponse({'message': 'Thành công'}, status = 200)
    else:
        return JsonResponse({'message': 'Lỗi trong quá trình tạo node'}, status = 400)

@permission_classes([IsAdmin])  
@api_view(['POST'])
def graph_data(request):
    data = request.data.get('neo4j')
    result = [1]
    if data:
        query = data
    else:
        query = "MATCH (n)-[r]->(m) RETURN n, properties(r) as r, m LIMIT 100"
    
    try:
        result = run_query(driver=driver,query=query)
    except Exception as e:
        print(e)
        return JsonResponse({'message': 'Lỗi câu query'}, status = 400)
    nodes = {}
    edges = []
    try:
        for record in result:
            n = record["n"]
            m = record["m"]
            r = record["r"]
            
            nodes[str(n["node_id"])] = {
                "id": str(n["node_id"]),
                "properties": dict(n)
            }

            nodes[str(m["node_id"])] = {
                "id": str(m["node_id"]),
                "properties": dict(m)
            }

            edges.append({
                "source": str(n["node_id"]),
                "target": str(m["node_id"]),
                "properties": r
            })

        return JsonResponse({
                "nodes": list(nodes.values()),
                "edges": edges
            }, status = 200)
    except Exception as e:
            print(e)
            return JsonResponse({"message": "Lỗi trả về"}, status = 400)

    