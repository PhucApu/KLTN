from django.urls import path
from api.views.getFile import get_pdf,getFile,dele_file
from api.views.component import process_pdf, search_components, bulk_update_components, del_components
from api.views.upFileViews import FileUploadView
from api.views.gTextView import create_gtext, update_gtext, delete_gtext, search_gtext, init_gtext
from api.views.concEle import get_concele_list, update_concele
from api.views.relEle import init_rel_conc,get_relele_list, update_relele
from api.views.gConc import suggest_gconc,get_gconc_list,update_gconc,init_gConc, update_similar_conc
from api.views.gRel import suggest_gRel2, init_gRel,search_grel,update_grel, update_similar_rel
from api.views.suggestConc import init_suggestconc, get_suggest_conc
from api.views.Neo4j import init_graph_data,graph_data
from api.views.suggerstRel import init_suggestrelation, get_suggest_rel
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from api.views.user import user_create,user_detail,user_update,search_users,me_detail,logout_view
from api.views.Ans import Ans
urlpatterns = [
    path('upload', FileUploadView.as_view(), name='file-upload'),
    path('files/<int:file_id>/', get_pdf, name='get-pdf'),
    path('delete-file/<int:id>/', dele_file, name='get-pdf'),
    path('delete-component/<int:id>', del_components, name='get_components'),
    path('process-pdf', process_pdf, name='process_pdf'), # xong rồi
    path('search-components',search_components , name='search_components'),
    path('getFile',getFile , name='getFile'), # xong rồi
    path('update-component',bulk_update_components , name='bulk_update_components'), # xong rồi
    path('create-gtext/', create_gtext, name='create_gtext'), #xong
    path('update-gtext/<int:id>/', update_gtext, name='update_gtext'), # xong
    path('delete-gtext/<int:id>/', delete_gtext, name='delete_gtext'), # xong
    path('gtext/search/', search_gtext, name='search_gtext'), 
    path('init-gtext/<int:idLaw>/', init_gtext, name='init_gtext'), # xong rồi    
    path('get-conc/', get_concele_list, name='get_concele_list'),  # xong
    path('init-rel-conc/<int:idLaw>/', init_rel_conc, name='init_rel_conc'),  # xong    
    # path('get-conc/', get_concele_list, name='init_rel_conc'),  # xong    
    path('update-conc/<int:id>/', update_concele, name='update_concele'), # xong
    path('suggest-concept/', suggest_gconc, name='suggest_gconc'), # xong
    path('get-rel/', get_relele_list, name='get_relele_list'), # xong
    path('update-rel/<int:id>/', update_relele, name='update_relele'), # xong
    path('suggest-relation/', suggest_gRel2, name='suggest_gRel'), # xong
    path('init-gconcept/<int:idLaw>/<int:idSuggest>/', init_suggestconc, name='init_suggestconc'), # xong
    path('init-grelation/<int:idLaw>/<int:idSuggest>/', init_suggestrelation, name='init_suggestrelation'), # xong
    path('init-grel/', init_gRel, name='init_gRel'), # xong
    path('search-grel/', search_grel, name='search_grel'), # xong
    path('update-grel/<int:grel_id>/', update_grel, name='update_grel'), # xong
    path('update-gconc/<int:gconc_id>/', update_gconc, name='update_gconc'), # xong
    path('search-gconc/', get_gconc_list, name='update_gconc'), # xong
    path('init-gconc/', init_gConc, name='init_gConc'), # xong
    path('init-graph/', init_graph_data, name='init_graph_data'), # xong
    path('graph-data/', graph_data, name='graph_data'), # xong
    path('get-suggest-conc/', get_suggest_conc, name='get_suggest_conc'), # xong
    path('get-suggest-rel/', get_suggest_rel, name='get_suggest_rel'), # xong
    path('update-similar-rel/', update_similar_rel, name='update_similar_rel'), # xong
    path('update-similar-conc/', update_similar_conc, name='update_similar_conc'), # xong
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user-create/', user_create, name='user_create'),
    path('user-update/', user_update, name='user_update'),
    path('user-detail/', user_detail, name='user_detail'),
    path('search-user/', search_users, name='search_users'),
    path('me-detail/', me_detail, name='me_detail'),
    path('logout/', logout_view, name='logout_view'),
    path('ans/', Ans, name='Ans'),




]
