from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from rest_framework.decorators import api_view
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
from ..utils.Neo4jSp import create_node, update_node_by_id, create_relationship,run_query, remove_descendants_from_relationships,remove_descendants,update_relationship
from ..utils.neo4j_driver import driver, close_driver

@csrf_exempt
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
            prop = {'node_id' : item.id ,'lstConC': item.lstConC, 'meaning': item.meaning,'descendants': item.descendants}
            create_node(driver=driver, properties=prop)
            item.updateNeo4j = 0
            item.save()
        
        lstNode = GConc.objects.filter(updateNeo4j = 2)
        for item in lstNode:
            prop = {'lstConC': item.lstConC, 'meaning': item.meaning,'descendants': item.descendants}
            update_node_by_id(driver=driver, node_id=item.id , properties=prop)
            item.updateNeo4j = 0
            item.save()
        return True
        
    except:
        return False
    
def relation():
    try:
        lstrel = gRel.objects.exclude(Q(update_concs=None)| Q(update_concs=[]))
        for item in lstrel:
            prop = {'relation_id' : item.id,'lstRel': item.lstRel, 'meaning': item.meaning,'descendants': item.descendants}
            for count in range(item.update_conco):
                create_relationship(driver=driver,start_node_id=item.update_concs[count], end_node_id=item.update_conco[count],rel_properties=prop)
            item.update_conco = []
            item.update_concs = []
            item.save()
        lstrel = gRel.objects.filter(updaterel = 1)
        for item in lstrel:
            for count in range(item.update_conco):
                prop = {'relation_id' : item.id,'lstRel': item.lstRel, 'meaning': item.meaning,'descendants': item.descendants}
                update_relationship(driver=driver,rel_id=item.id,rel_properties=prop)
            item.update_conco = []
            item.update_concs = []
            item.updaterel=0
            item.save()
        return True
    except:
        return False
    
@csrf_exempt
@api_view(['GET'])
def init_graph_data(request):
    if node() and relation():
        return JsonResponse({'message': 'Thành công'}, status = 200)
    else:
        return JsonResponse({'message': 'Lỗi trong quá trình tạo node'}, status = 400)

@csrf_exempt
@api_view(['GET'])
def graph_data(request):
    data = request.data.get('neo4j')
    if data:
        query = data
    else:
        query = "MATCH (n)-[r]->(m) RETURN n, r, m LIMIT 50"
    try:
        result = run_query(query)
    except:
        JsonResponse({'message': 'Lỗi câu query'}, status = 400)
    nodes = {}
    edges = []

    for record in result:
        n = record["n"]
        m = record["m"]
        r = record["r"]

        nodes[str(n.id)] = {
            "id": str(n.id),
            "label": n.labels[0],
            "properties": dict(n)
        }

        nodes[str(m.id)] = {
            "id": str(m.id),
            "label": m.labels[0],
            "properties": dict(m)
        }

        edges.append({
            "source": str(n.id),
            "target": str(m.id),
            "label": r.type,
            "properties": dict(r)
        })

    return JsonResponse({
        "nodes": list(nodes.values()),
        "edges": edges
    }, status = 200)


    