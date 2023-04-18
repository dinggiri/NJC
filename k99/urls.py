from django.urls import path
from . import views

app_name = 'k99'

urlpatterns = [
    path('', views.main, name='main'),
    # 사례등록 - 실전사례
    path('adding/', views.adding, name = "adding"),
    path('adding/realexamplemanage/', views.realexamplemanage, name = "realexamplemanage"),
    path('adding/realexamplemanage/add/', views.realexampleadd, name = "realexampleadd"),
    path('adding/realexamplemanage/adding/', views.addpost, name = "addpost"),
    path('adding/realexamplemanage/adding2/', views.addrealexample, name = "addrealexample"),
    # 사례등록 - 질문답변
    path('adding/qnamanage/', views.qnamanage, name = "qnamanage"),
    path('adding/qnamanage/add/', views.qnaadd, name = "qnaadd"),
    path('adding/qnamanage/adding/', views.addpost_qna, name = "addpost_qna"),
    path('adding/qnamanage/adding2/', views.addqna, name = "addqna"),
    # 사례등록 - 코멘트 추가
    path('adding/addcomment/', views.addcomment, name = "addcomment"),
    # 로그 다운로드
    path('exportlog/', views.log_export, name='log_export'),  # 엑셀 파일 다운로드
    # product
    path('yearselect/', views.select_year, name='yearselect'),
    path('product/<int:year>/', views.product),
    path('product/allyear/', views.allyearproduct),
    path('product/<int:year>/<int:product_id>/', views.eachyeardetail),
    path('product/allyear/<int:product_id>/', views.allyeardetail),
    # 상품및회원사관리
    path('manage/', views.manage),
    path('manage/product', views.manageproduct),
    path('manage/allproduct', views.allproduct),
    path('manage/reviseproduct', views.reviseproduct, name="reviseProduct"),
    path('manage/revised', views.revise, name="revise"),
    path('manage/customer', views.managecustomer, name="add"),
    path('manage/allcustomer', views.allcustomer),
    path('manage/revisecustomer', views.revisecustomer, name="reviseCustomer"),
    path('manage/revisedcust', views.revisecust, name="revisecust"),
    path('manage/deletecust', views.deletecustomer, name="deleteCustomer"),
    # 회원사관리
    path('customer/', views.searchcust),
    path('customer/search', views.search, name='search'),
    # 구매내역입력
    path('buy', views.write, name="write"),
    path('deletebuy', views.deletebuy, name="deletebuy"),
    path('_deletebuy', views._deletebuy, name="_deletebuy"),
    path('export', views.excel_export, name='excel_export'),  # 엑셀 파일 다운로드

    path('recipetype/', views.recipetype, name='recipetype'),
    path('mix/', views.mix, name='mix'),
    path('clothes/', views.clothes, name='clothes'),
    path('material/', views.materialType, name='materialType'),
    path('color/', views.color, name='color'),
    path('issue/', views.issue, name='issue'),
    path('luxury/', views.luxury, name='luxury'),
    path('keyword/', views.keyword, name='keyword'),
    path('recipe/', views.recipe, name='recipe'),

    path('qna/', views.qna, name='qna'),
    path('qna/category/', views.qnaCategory, name='qna_category'),
    path('qna/category/<int:qna_id>/', views.detail, name='qna_detail'),
]