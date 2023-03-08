from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import *
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
from django.db.models import Sum, Count, Q
from django.db.models.functions import TruncMonth, TruncYear
from django.http import Http404, HttpResponse
from urllib.parse import quote
import io
import xlsxwriter
import ast
import pandas as pd
from datetime import datetime, timedelta

def makeBool(str):
    if str is None:
        return str
    elif str.lower() == 'true':
        return True
    elif str.lower() == 'false':
        return False
    else:
        return str

def makeBoolFromYN(str):
    if str is None:
        return str
    elif str.lower() == 'yes':
        return True
    elif str.lower() == 'no':
        return False
    elif str.lower() == 'no_white':
        return False
    else:
        return str

def listOrNone(var):
    if type(var) == list:
        return var
    elif var is not None:
        var = var.replace("''", "'").replace('"', '').replace(' ', '')
        return ast.literal_eval(var)
    else:
        return None

def listClean(l):
    """
    리스트를 받아 ,로 구분된 것으로 바꿔주는 코드
    """
    string = str(l)
    string = string.replace(" ", "").replace("[", "").replace("]", "").replace("'", "").replace("None", "")
    return string

def REpostObjRevision(obj):
    postObj = []
    for post in obj:
        if type(post) == int:
            post = Posts.objects.get(pid=post)
        pvurl = listOrNone(post.pvurl)
        postObj.append([post, pvurl])
    return postObj

def QApostObjRevision(nprof, prof):
    postObj = {}
    for pid in prof:
        tmp_obj = QnA.objects.get(pid_id=pid)
        subject = tmp_obj.subject
        prof = tmp_obj.prof
        if type(pid) == int:
            post = Posts.objects.get(pid=pid)
        cdate = post.create_date
        postObj[pid] = [post, cdate, subject, prof]
    sorted_dict = sorted(postObj.items(), key=lambda item: item[1][1], reverse=True)
    sorted_list1 = [[x[1][0], x[1][2], x[1][3]] for x in sorted_dict]  # [post object, post subject, prof bool]
    postObj = {}

    for pid in nprof:
        tmp_obj = QnA.objects.get(pid_id=pid)
        subject = tmp_obj.subject
        prof = tmp_obj.prof
        if type(pid) == int:
            post = Posts.objects.get(pid=pid)
        cdate = post.create_date
        postObj[pid] = [post, cdate, subject, prof]
    sorted_dict = sorted(postObj.items(), key=lambda item: item[1][1], reverse=True)
    sorted_list2 = [[x[1][0], x[1][2], x[1][3]] for x in sorted_dict]  # [post object, post subject, prof bool]

    postObj = sorted_list1 + sorted_list2
    return postObj

# def _getSearchCount(results, criterion):
#     if type(results) == pd.core.frame.DataFrame:
#         total_df = results.sort_values(by=['score'], ascending=False)
#         ### Set minimum(10)
#         if len(total_df) > 10:
#             # 역치? 설정
#             df = total_df[total_df.score >= criterion]
#             if len(df) <= 10:
#                 df = total_df
#         else:
#             df = total_df
#         results_pid = list(df['pid_id'])
#         count = len(df)
#     else:
#         results_pid = [q.pid for q in results]
#         count = results.count()
#     dict = {
#         'count': count,
#         'pid': results_pid,
#     }
#     return dict

def _getSearchCount(results, criterion):
    if type(results) == pd.core.frame.DataFrame:
        # print(f'criterion: {criterion}')
        total_df = results.sort_values(by=['score'], ascending=False)
        df = total_df[total_df.score >= criterion]
        # print(df)
        results_pid = list(df['pid_id'])
        count = len(df)
    else:
        results_pid = [q.pid for q in results]
        count = results.count()
    dict = {
        'count': count,
        'pid': results_pid,
    }
    return dict

def getSearchCount(stage, log):
    ### 중간 단계 확인!!
    criterion_1 = [1000, 70, 40, 20, 0]  # clothes
    criterion_2 = [2000, 140, 100, 70, 0]  # material

    criterion_3 = [3000, 220, 160, 100, 0]  # issue
    criterion_4 = [500, 0]  # issue_detail
    criterion_5 = [10000, 0]  # luxury

    criterion = 0

    ### 1. 혼합세탁
    mix = log.mix
    mix_white = log.mix_white
    results = Realexamples.objects.filter(mix=mix, mix_white=mix_white)
    if stage == 'mix':
        return _getSearchCount(results, criterion)

    ### 2. 세탁물종류
    clothes = listOrNone(log.clothes)
    df = pd.DataFrame(list(results.values()))
    df.insert(df.shape[1], 'score', 0)

    def _Clothes(item):
        score = 0
        dct = {'상의': [], '하의': [], '원피스': [], '겉옷': [], '패딩': [], '가방': [], '신발': [], '모자': [], '한복': [], '침구류': [],
               '기타': []}
        for c in clothes:
            if c in item:
                dct[c].append(criterion_1[0])
            if c == '겉옷':
                if '패딩' in item: dct['패딩'].append(criterion_1[1])
                if '상의' in item: dct['상의'].append(criterion_1[2])
            elif c == '상의':
                if '하의' in item: dct['하의'].append(criterion_1[1])
                if '겉옷' in item: dct['겉옷'].append(criterion_1[2])
            elif c == '하의':
                if '상의' in item: dct['상의'].append(criterion_1[1])
            elif c == '한복':
                if '원피스' in item: dct['원피스'].append(criterion_1[2])
                if '상의' in item: dct['상의'].append(criterion_1[3])
                if '하의' in item: dct['하의'].append(criterion_1[3])
            elif c == '원피스':
                if '상의' in item: dct['상의'].append(criterion_1[3])
                if '하의' in item: dct['하의'].append(criterion_1[3])

        for it, scores in dct.items():
            if len(dct[it]) != 0:
                score += max(dct[it])
        return score

    df['score'] += df['clothes'].apply(_Clothes)
    criterion += criterion_1[0] * len(clothes) * 0.5

    if stage == 'clothes':
        return _getSearchCount(df, criterion)

    ### 3. 소재
    if (not mix) and (clothes[0] != '가방'):
        material = listOrNone(log.material)
        df.insert(1, 'material', 0)
        df['material_out'] = df['material_out'].apply(lambda x: x.split(',') if x != '없음' else [])
        df['material_in'] = df['material_in'].apply(lambda x: x.split(',') if x != '없음' else [])
        df['material'] = df['material_out'] + df['material_in']
        # 혼방 점수 줄거면 여기서 len() > 1 이면 혼방취급
        df['material'] = df['material'].apply(lambda x: list(set(x)))

        def _Material(item):
            score = 0
            dct = {'면': [], '린넨': [], '마': [], '레이온': [], '모달': [], '모': [], '실크': [], '나일론': [], '폴리에스테르': [],
                   '아크릴': [], '아세테이트': [], '모피': [], '스웨이드': [], '동물털': [], '인조가죽': [], '폴리우레탄': [], '솜': [], '기타': [],
                   '모름': []}
            for m in material:
                if m in item:
                    if m == '모름':
                        continue
                    else:
                        dct[m].append(criterion_2[0])
                if '모름' in item:
                    dct['모름'].append(criterion_2[3])

            for it, scores in dct.items():
                if len(dct[it]) != 0:
                    score += max(dct[it])
            return score

        df['score'] += df['material'].apply(_Material)
        material_cnt = len([x for x in material if x != '모름'])
        criterion += criterion_2[0] * material_cnt * 0.8

        if stage == 'material':
            return _getSearchCount(df, criterion)


    ### 4. 색상
    if not mix:
        total_color = listOrNone(log.color)
        color = total_color[0]
        if '배색' in total_color:
            comb_colors = True
        else:
            comb_colors = False
        if '프린팅' in total_color:
            printing = True
        else:
            printing = False

        # df['score'] += df['color'].apply(lambda x: criterion_1[0] if x == color else criterion_1[4])
        df = df[df['color'] == color]
        df['score'] += df['comb_colors'].apply(lambda x: criterion_1[0] if x == comb_colors else criterion_1[2])
        df['score'] += df['printing'].apply(lambda x: criterion_1[0] if x == printing else criterion_1[2])
        criterion += criterion_1[0]*2

        if stage == 'color':
            return _getSearchCount(df, criterion)

    ### 5. 세탁사유
    issue = listOrNone(log.issue)
    issue_detail = listOrNone(log.issue_detail)  # [[유색오염],[생활얼룩],[기타]]

    def _Issue(item):
        score = 0
        dct = {'이염': [], '유색오염': [], '음식물': [], '황변': [], '곰팡이': [], '기름': [], '생활얼룩': [], '변색': [], '탈색': [], '기타': [], '모름': [],
               '없음': []}
        for i in issue:
            if i in item:
                if i == '모름':
                    continue
                else:
                    dct[i].append(criterion_3[0])
            if '모름' in item:
                dct['모름'].append(criterion_3[3])
            if i == '유색오염':
                if '생활얼룩' in item: dct['생활얼룩'].append(criterion_3[1])
            elif i == '생활얼룩':
                if '유색오염' in item: dct['유색오염'].append(criterion_3[1])

        for it, scores in dct.items():
            if len(dct[it]) != 0:
                score += max(dct[it])
        return score

    def _IssueDetail(item):
        score = 0
        dct = {'잉크': [], '화장품': [], '페인트': [], '그을음': [], '염색약': [], '기타유색오염': [], '체액': [], '빗물': [], '녹물': [],
               '접착제': [], '세제자국': [], '기타생활얼룩': [], '냄새': [], '복원': [], '보색': [], '기타': []}
        if item is not None:
            for iss in issue_detail:
                if len(iss) != 0:
                    for d in iss:
                        if d in item:
                            dct[d].append(criterion_4[0])

            for it, scores in dct.items():
                if len(dct[it]) != 0:
                    score += max(dct[it])
        return score

    df['score'] += df['issue'].apply(_Issue)
    df['score'] += df['issue_detail'].apply(_IssueDetail)
    issue_cnt = len([x for x in issue if x != '모름'])
    criterion += (criterion_3[0]*issue_cnt + criterion_4[0]*(len(issue_detail[0])+len(issue_detail[1])+len(issue_detail[2])))*0.8

    if stage == 'issue':
        return _getSearchCount(df, criterion)

    ### 6. 명품
    luxury = log.luxury
    df = df[df['luxury'] == luxury]
    # df['score'] += df['luxury'].apply(lambda x: criterion_5[0] if x == luxury else criterion_5[1])

    if stage == 'luxury':
        # criterion += criterion_5[0]
        return _getSearchCount(df, criterion)

def _getQACount(df, namelist):
    tdf = df[df['category'].isin(namelist)]
    tdf_nonprof = tdf[tdf['prof'] == False]
    tdf_prof = tdf[tdf['prof'] == True]
    results_nprof_pid = list(tdf_nonprof['pid_id'])
    results_prof_pid = list(tdf_prof['pid_id'])
    count = len(tdf)
    dict = {
        'count': count,
        'pid_nprof': results_nprof_pid,
        'pid_prof': results_prof_pid,
    }
    return dict

def getQACount(category):
    results = QnA.objects.all()
    df = pd.DataFrame(list(results.values()))

    if category == 'recipe':
        return _getQACount(df, ['세탁방법', '세탁방법, 세탁약품'])
    elif category == 'chemical':
        return _getQACount(df, ['세탁약품', '세탁방법, 세탁약품'])
    elif category == 'tool':
        return _getQACount(df, ['도구사용법'])
    elif category == 'problem':
        return _getQACount(df, ['문제발생원인'])
    elif category == 'etc':
        return _getQACount(df, ['기타'])

def getmonth(buy_month, query):
    """
    월 계산을 위한 간단한 함수입니다.
    :param buy_month: 구매한 상품의 개월(queryset 형태)이저장되어있는 데이터프레임입니다.

    :param query: 통계를 내고자 하는 query입니다. query는 "cnt"- 구매건수, "sum"-구매량합 입니다.
    :return: 계산이 완료된 리스트. 1월-12월까지의 구매건수 또는 구매량이 저장되어 있습니다.
    """
    base = [0] * 12
    for bm in buy_month:
        try:
            base[bm["month"].month - 1] = bm[query]
        except IndexError:
            continue
    return base

def checkregular(customer):
    """
    정회원 검사를 위한 함수입니다. 모든 buy 기록과 customer 기록을 대조합니다.

    :param customer: customer의 querydict입니다.
    :return: 정회원인 경우 True, 아닌 경우 False
    """
    kid = customer.kid
    reg = customer.regular
    cdate = customer.cdate
    if not cdate: # 가입 날짜 정보가 없는 경우 False 리턴
        return False
    # cdate = cdate.replace(tzinfo=KST)
    ########################################
    ######## 2022년 1월 1일 전 가입자 #########
    ####### 그리고, 연장이 되지 않은 사람 #######
    if cdate < datetime(2022, 1, 1) : # 2022년 1월 1일 전 가입자
        if not customer.edate:
            customer.edate = cdate + timedelta(days=364) # 364일 추가
        if customer.edate < datetime(2022, 12, 31):
            try:
                kbuys = Buy.objects.filter(Q(kid=kid) & (Q(pid=4) | Q(pid=10))).order_by('-bdate') # 해당 번호 사람이 buy한 것들 중 마지막
                kbuys_amount = sum([kb.bamount for kb in kbuys])
                if kbuys_amount < 10:
                    customer.residual = 10 - kbuys_amount
                    customer.regular = False
                else:
                    plus = kbuys_amount // 10
                    residual = kbuys_amount % 10
                    customer.edate = customer.cdate + (2 + plus) * timedelta(days=182) # 365일 추가
                    # if not residual:
                    #     residual = 20
                    customer.residual = residual

            except IndexError:
                customer.residual = 10
                customer.regular = False
    ########  연장이 이미 완료된 사람 #########
    ##### 회원종료 만료일로부터 12개월 동안의 데이터를 추출
        else:
            try:
                # kbuys = Buy.objects.filter(Q(kid=kid) & (Q(pid=4) | Q(pid=10)) & Q(bdate__range=[customer.edate - timedelta(days=365), customer.edate])).order_by('-bdate')
                kbuys = Buy.objects.filter(Q(kid=kid) & (Q(pid=4) | Q(pid=10))).order_by('-bdate')  # 해당 번호 사람이 buy한 것들 중 마지막
                kbuys_amount = sum([kb.bamount for kb in kbuys])
                if kbuys_amount < 10:
                    customer.residual = 10 - kbuys_amount
                    customer.regular = False
                else:
                    # customer.edate = customer.edate + timedelta(days=365) # 365일 추가
                    plus = kbuys_amount // 10
                    residual = kbuys_amount % 10
                    customer.edate = customer.cdate + (2 + plus) * timedelta(days=182)  # 182일 추가
                    # if not residual:
                    #     residual = 0
                    customer.regular = True
                    customer.residual = residual

            except IndexError:
                customer.regular = False
                customer.residual = 10

    #########################################
    ######## 2022년 1월 1일 이후 가입자 #########
    ####### 그리고, 연장이 되지 않은 사람 #######
    else:
        if not customer.edate:
            customer.edate = cdate + timedelta(days=364) # 364일 추가
        if customer.edate < cdate + timedelta(days=360):
            try:
                kbuys = Buy.objects.filter(Q(kid=kid) & (Q(pid=4) | Q(pid=10))).order_by('-bdate') # 해당 번호 사람이 buy한 것들 중 마지막
                kbuys_amount = sum([kb.bamount for kb in kbuys])
                if kbuys_amount < 20:
                    customer.residual = 20 - kbuys_amount
                    customer.regular = False
                else:
                    # customer.edate = customer.cdate + timedelta(days=365) # 365일 추가
                    plus = kbuys_amount // 20
                    residual = kbuys_amount % 20
                    customer.edate = customer.cdate + (1 + plus) * timedelta(days=365)
                    customer.regular = True
                    customer.residual = residual

            except IndexError:
                customer.regular = False
                customer.residual = 20
                # return False
                ########  연장이 이미 완료된 사람 #########
                ##### 회원종료 만료일로부터 12개월 동안의 데이터를 추출
        else:
            try:
                # kbuys = Buy.objects.filter(Q(kid=kid) & (Q(pid=4) | Q(pid=10)) & Q(bdate__range=[customer.edate - timedelta(days=365), customer.edate])).order_by('-bdate')
                kbuys = Buy.objects.filter(Q(kid=kid) & (Q(pid=4) | Q(pid=10))).order_by('-bdate')
                kbuys_amount = sum([kb.bamount for kb in kbuys])
                if kbuys_amount < 10:
                    customer.residual = 10 - kbuys_amount
                    customer.regular = False
                else:
                    plus = kbuys_amount // 10
                    residual = kbuys_amount % 10
                    customer.edate = customer.cdate + (2 + plus) * timedelta(days=182)  # 365일 추가
                    # if not residual:
                    #     residual = 0
                    customer.residual = residual
                    # customer.edate = customer.edate + timedelta(days=365)  # 365일 추가
            except IndexError:
                customer.regular = False
                customer.residual = 10

        # 섬유향균제와 탈취스프레이 총양 20kg 이상이어야 정회원 자격 얻음


    if customer.edate < customer.cdate:
        customer.regular = False
        customer.save()
        return False
    if customer.edate < datetime.today():
        customer.regular = False
        customer.save()
        return False
    else:
        customer.regular = True
        customer.save()
        return True

    return True


### views.index 합치기
@login_required(login_url='common:login')
def main(request):
    username = request.user.username
    if username == 'admin':
        return render(request, 'k99/admin/main.html')
        #return render(request, 'k99/main.html')
    else:
        context = {
            'username': username,
        }
        return render(request, 'k99/main.html', context)

@login_required(login_url='common:login')
def select_year(request):
    """
    연도 선택 홈페이지입니다. 여기서 연도를 선택한 뒤, 상품을 선택하고 통계를 볼 수 있습니다.
    """
    all_year = Buy.objects.all()\
        .annotate(year=TruncYear("bdate")).values("year")
    years = list(set([b['year'].year for b in all_year]))
    context = {
        'years' : years
    }
    return render(request, 'k99/admin/yearselect.html', context)

#### Product
@login_required(login_url='common:login')
def product(request, year):
    """
    상품 선택 페이지입니다. 선택된 연도에 대해 상품을 선택할 수 있습니다.

    :param year: integer, 선택된 특정 연도
    """
    products = Product.objects.all()
    context = {
        'products': products,
        'year': year
    }
    return render(request, 'k99/admin/product.html', context)

@login_required(login_url='common:login')
def allyearproduct(request):
    """
    전체 년도 상품 선택 페이지입니다. 전체 연도 통계 분석을 보기 위해 상품을 선택할 수 있습니다.
    """
    products = Product.objects.all()
    context = {
        'products': products,
        'year' : False
    }
    return render(request, 'k99/admin/product.html', context)

@login_required(login_url='common:login')
def eachyeardetail(request, year, product_id):
    specific_product = Product.objects.get(pid=product_id)
    buy_month = Buy.objects.filter(pid=product_id, bdate__year=year)\
        .annotate(month=TruncMonth("bdate")).values("month")\
        .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("month", "cnt", "sum")
    buy_month_cnt = getmonth(buy_month, "cnt")
    buy_month_sum = getmonth(buy_month, "sum")
    buy_month_price = [c * specific_product.pprice for c in buy_month_cnt]
    base_month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    month_list = [str(year) + month for month in base_month]
    context = {
        'product' : specific_product,
        'buy_month_cnt' : buy_month_cnt,
        'buy_month_sum': buy_month_sum,
        'buy_month_price' : buy_month_price,
        'buy_month' : buy_month,
        'month_list' : month_list
    }
    return render(request, 'k99/admin/product_detail.html', context)

@login_required(login_url='common:login')
def allyeardetail(request, product_id):
    specific_product = Product.objects.get(pid=product_id)
    all_year = Buy.objects.filter(pid=product_id) \
        .annotate(year=TruncYear("bdate")).values("year")
    buy_year = Buy.objects.filter(pid=product_id) \
        .annotate(year=TruncYear("bdate")).values("year") \
        .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("year", "cnt", "sum")
    years = list(set([b['year'].year for b in all_year]))
    buy_year_cnt = [b['cnt'] for b in buy_year]
    buy_year_sum = [b['sum'] for b in buy_year]

    buy_year_price = [c * specific_product.pprice for c in buy_year_cnt]
    context = {
        'product' : specific_product,
        'buy_year_cnt': buy_year_cnt,
        'buy_year_sum': buy_year_sum,
        'buy_year_price': buy_year_price,
        'years' : years
    }
    return render(request, 'k99/admin/product_allyeardetail.html', context)

#### Manage

@login_required(login_url='common:login')
def manage(request):
    context = {}
    return render(request, 'k99/admin/manage.html', context)

@login_required(login_url='common:login')
def manageproduct(request):
    if request.method == 'POST':
        try:
            Product.objects.create(
                pid = Product.objects.order_by('-pk')[0].pid + 1,
                pname = request.POST['productname'],
                pprice = request.POST['productprice']
            )
        except:
            context = {}
            return render(request, 'k99/admin/manageproduct.html', context)
        products = Product.objects.all()
        context = {
            'products' : products
        }
        return render(request, 'k99/admin/allproduct.html', context)
    context = {}
    return render(request, 'k99/admin/manageproduct.html', context)

@login_required(login_url='common:login')
def allproduct(request):
    products = Product.objects.order_by('pid')
    context = {
        'products' : products
    }
    return render(request, 'k99/admin/allproduct.html', context)

@login_required(login_url='common:login')
def reviseproduct(request):
    try:
        product = Product.objects.get(pid = int(request.POST['rev_productid']))
        context = {
            'product': product,
            'error' : False,
            'message' : "정상 수행"
        }
    except:
        context = {
            'product': None,
            'error' : True,
            'message' : "해당 id에 맞는 상품이 없습니다."
        }
    return render(request, 'k99/admin/reviseproduct.html', context)

@login_required(login_url='common:login')
def revise(request):
    if request.method == 'POST':
        product = Product.objects.get(pid=int(request.POST['revproductid']))
        product.pname = request.POST['revpname']
        product.pprice = request.POST['revpprice']
        product.save()
    products = Product.objects.order_by('pid')
    context = {
        'products': products
    }
    return render(request, 'k99/admin/allproduct.html', context)

@login_required(login_url='common:login')
def managecustomer(request):
    if request.method == "GET":
        customer = Customer.objects.all()
        context = {
            'customers': customer
        }
        return render(request, 'k99/admin/managecustomer.html', context)
    elif request.method == "POST":
        username = request.POST.get('IDinput')
        password = request.POST.get('PWinput').upper()
        kname = request.POST.get('knameinput')
        kid = request.POST.get('KIDinput')
        doe = request.POST.get('doeinput')
        sigungu = request.POST.get('sigunguinput')
        dong = request.POST.get('donginput')
        sangse = request.POST.get('sangseinput')
        sname = request.POST.get('snameinput')
        note = request.POST.get('noteinput')
        zipcode = request.POST.get('zipcodeinput')
        cdate = request.POST.get('cdateinput')
        # print(cdate)currdate = datetime.datetime.strptime(str_datetime, '%Y-%m-%d %H:%M:%S')
        regular = makeBool(request.POST.get('regularinput'))
        if regular:
            edate = datetime.strptime(cdate, '%Y-%m-%d') + timedelta(days=365)  # 365일 추가
        else:
            edate = datetime.strptime(cdate, '%Y-%m-%d') # 추가 없음
        cphone = request.POST.get('cphoneinput')
        email = 0
        a = CustomerManager()
        a.create_customer(username=username, password=password, kname=kname, kid=kid, doe=doe, sigungu=sigungu,
                                        dong=dong,sangse=sangse, sname=sname, note=note, zipcode=zipcode, cdate=cdate,
                                        edate = edate,
                                        regular=regular, cphone=cphone, email=email)

        customer = Customer.objects.all()
        context = {
            'customers': customer
        }
        return render(request, 'k99/admin/allcustomer.html', context)

    customer = Customer.objects.all()
    context = {
        'customers' : customer
    }
    return render(request, 'k99/admin/managecustomer.html', context)

@login_required(login_url='common:login')
def allcustomer(request):
    customers = Customer.objects.order_by('kid')
    for customer in customers:
        checkregular(customer)
        customer.save()
    context = {
        'customers' : customers
    }
    return render(request, 'k99/admin/allcustomer.html', context)

@login_required(login_url='common:login')
def revisecustomer(request):
    try:
        customer = Customer.objects.get(kid = int(request.POST['rev_customerid']))
        context = {
            'customer': customer,
            'error' : False,
            'message' : "정상 수행"
        }
    except:
        context = {
            'customer': None,
            'error' : True,
            'message' : "해당 id에 맞는 회원사가 없습니다."
        }
    return render(request, 'k99/admin/revisecustomer.html', context)

@login_required(login_url='common:login')
def revisecust(request):
    if request.method == 'POST':
        customer = Customer.objects.get(kid=int(request.POST['revkid']))
        customer.kname = request.POST['revkname']
        customer.doe = request.POST['revdoe']
        customer.sigungu = request.POST['revsigungu']
        customer.dong = request.POST['revdong']
        customer.sangse = request.POST['revsangse']
        customer.sname = request.POST['revsname']
        customer.cphone = request.POST['revcphone']
        customer.zipcode = request.POST['revzipcode']
        customer.regular = request.POST['revregular']
        if request.POST['revedate']:
            customer.edate = datetime.strptime(request.POST['revedate'], '%Y-%m-%d')
        else:
            customer.edate = datetime.strptime(request.POST['revedate_read'].replace('오전','AM').replace('오후','PM') , '%Y년 %m월 %d일 %H:%M %p')
        # print(request.POST['revedate'])
        if request.POST['beforerev'] == "False" and request.POST['revregular'] == "True": # 정회원으로 변경시킨 경우 12개월 연장
            customer.edate = customer.edate + timedelta(days=365)  # 365일 추가
            customer.set_password("K" + request.POST['revpassword'][1:])
            customer.real_pw = "K" + request.POST['revpassword'][1:]
        customer.save()
    customers = Customer.objects.order_by('kid')
    context = {
        'customers': customers
    }
    return render(request, 'k99/admin/allcustomer.html', context)

@login_required(login_url='common:login')
def deletecustomer(request):
    if request.method == 'POST':
        try:
            customer = Customer.objects.get(kid=int(request.POST['del_customerid']))
            customer.delete()
            customers = Customer.objects.order_by('kid')
            context = {
                'customers': customers
            }
        except:
            customers = Customer.objects.order_by('kid')
            context = {
                'customers': customers
            }
    return render(request, 'k99/admin/allcustomer.html', context)

@login_required(login_url='common:login')
def searchcust(request):
    customers = Customer.objects.all()
    all_year = Buy.objects.filter() \
        .annotate(year=TruncYear("bdate")).values("year")
    products = Product.objects.all()
    years = list(set([b['year'].year for b in all_year]))
    context = {
        'customers' : customers,
        'years' : years,
        'products' : products
    }
    return render(request, 'k99/admin/searchcust.html', context)

@login_required(login_url='common:login')
def search(request):
    if request.method == 'POST':
        #### POST에서 갖고옴 ###
        # kid
        kid = request.POST['searched']
        # 연간검색/월간검색 구분
        if request.POST['choice'] == 'month':
            month = True
            try: # 월검색인 경우, 연도 구분
                year = request.POST['years']
            except:
                context = {'error': True, 'message': "올바른 년도를 선택해주세요."}
                return render(request, 'k99/admin/searched.html', context)
        else:
            month = False # 연간검색
        # 상품 id
        try:
            products = Product.objects.all()
            pnames = [p.pname for p in products]
            product_id = request.POST['product']
            if product_id != "all":
                specific_product = Product.objects.get(pid=product_id)
            else:
                specific_product = None
        except:
            context = {'error': True, 'message': "올바른 상품을 선택해주세요."}
            return render(request, 'k99/admin/searched.html', context)
        ######################


        # 고객 정보
        try:
            custinfo = Customer.objects.get(kid=kid)
        except:
            context = {'error' : True, 'message' : "존재하지 않는 k번호입니다. 다시 검색해주세요"}
            return render(request, 'k99/admin/searched.html', context)

        if month:  # 월간검색
            month_flag = True
            if product_id == "all": # 전체 검색
                allbuys = Buy.objects.filter(kid=kid, bdate__year=year) \
                    .annotate(month=TruncMonth("bdate")).values("month") \
                    .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("month", "cnt", "sum")
            else: # 특정 상품 검색
                allbuys = Buy.objects.filter(kid=kid, pid=product_id, bdate__year=year) \
                    .annotate(month=TruncMonth("bdate")).values("month") \
                    .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("month", "cnt", "sum")
            buy_cnt = getmonth(allbuys, "cnt")
            buy_sum = getmonth(allbuys, "sum")
            ### 금액계산
            if specific_product: # 상품이 하나 지정된 경우
                buy_all_cnt = None
                buy_price = [b * specific_product.pprice for b in buy_cnt]
            else: # 전체 상품이 선택된 경우
                products = Product.objects.all()
                buy_price = [0] * len(products)
                buy_all_cnt = []
                for product in products:
                    buy_tmp_cnt = getmonth(allbuys, "cnt")
                    buy_product_cnt = Buy.objects.filter(kid=kid, pid=product.pid, bdate__year=year) \
                        .annotate(month=TruncMonth("bdate")).values("month") \
                        .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("month", "cnt", "sum")
                    _cnt = getmonth(buy_product_cnt, "cnt")
                    buy_all_cnt.append(_cnt)
                    buy_price_tmp = [b * product.pprice for b in buy_tmp_cnt]
                    buy_price = [x + y for x, y in zip(buy_price, buy_price_tmp)]
                buy_all_cnt = [list(x) for x in zip(*buy_all_cnt)]
            base_month = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            month_list = [str(year) + month for month in base_month]
        else:  # 연간검색
            all_year = Buy.objects.filter() \
                    .annotate(year=TruncYear("bdate")).values("year")
            years = list(set([b['year'].year for b in all_year]))
            # 상품이 하나 지정된 경우
            if specific_product:
                allbuys = Buy.objects.filter(kid=kid, pid=product_id) \
                    .annotate(year=TruncYear("bdate")).values("year") \
                    .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("year", "cnt", "sum")

            else: # 전체 상품이 선택된 경우
                allbuys = Buy.objects.filter(kid=kid) \
                    .annotate(year=TruncYear("bdate")).values("year") \
                    .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("year", "cnt", "sum")
            buy_cnt = [b['cnt'] for b in allbuys]
            buy_sum = [b['sum'] for b in allbuys]
            if specific_product:
                buy_price = [b * specific_product.pprice for b in buy_cnt]
                buy_all_cnt = None
            else: #전체 상품이 선택된 경우
                buy_all_cnt = []
                for _ in years:
                    buy_all_tmp_cnt = []
                    products = Product.objects.all()
                    buy_price = [0] * len(products)
                    for product in products:
                        buy_product_cnt = Buy.objects.filter(kid=kid, pid=product.pid) \
                            .annotate(year=TruncYear("bdate")).values("year") \
                            .annotate(cnt=Count("bid"), sum=Sum("bamount")).values("year", "cnt", "sum")
                        try:
                            buy_all_tmp_cnt.append(buy_product_cnt[0]["cnt"])
                        except:
                            buy_all_tmp_cnt.append(int(0))
                        buy_tmp_cnt = [b['cnt'] for b in allbuys]
                        buy_price_tmp = [b * product.pprice for b in buy_tmp_cnt]
                        buy_price = [x + y for x, y in zip(buy_price, buy_price_tmp)]
                buy_all_cnt.append(buy_all_tmp_cnt)
            month_list = years
            month_flag = False
        context ={
            'product_list': pnames,
            'product' : specific_product,
            'month_list': month_list,
            'buy_cnt': buy_cnt,
            'buy_all_cnt' : buy_all_cnt,
            'buy_sum': buy_sum,
            'buy_price' : buy_price,
            'month_flag' : month_flag,
            'error': False,
            'customer': custinfo,
            'buys': allbuys,
            'month': month,
            'message': "정상 수행"
        }
    else:
        raise Http404("Error occured")
    return render(request, 'k99/admin/searched.html', context)

@login_required(login_url='common:login')
def write(request):
    context = {}
    if request.method == 'POST' and request.POST['buykid']:
        # 고객 정보 가져옴
        try:
            customer = Customer.objects.get(kid=int(request.POST['buykid']))
        except:
            context = {
                'todaybuy': None,
                'customer' : None,
                'product' : None,
                'bamount' : None,
                'error': True,
                'message': "해당 id에 맞는 회원사가 없습니다."
            }
            return render(request, 'k99/admin/buy.html', context)
        # 상품 정보 가져옴
        if not customer.regular:
            context = {
                'todaybuy': None,
                'customer': customer,
                'product': None,
                'bamount': None,
                'error': True,
                'message': f"{request.POST['buykid']}번 회원사는 현재 준회원 상태인 회원사입니다."
            }
            return render(request, 'k99/admin/buy.html', context)
        try:
            product = Product.objects.get(pid=int(request.POST['buypid']))
        except:
            context = {
            'todaybuy': None,
            'customer' : None,
            'product' : None,
            'bamount' : None,
            'error': True,
            'message': "해당 id에 맞는 상품이 존재하지 않습니다."
            }
            return render(request, 'k99/admin/buy.html', context)

        # 구매수량 가져옴
        try:
            bamount = int(request.POST['buyamount'])
        except:
            context = {
                'todaybuy': None,
                'customer': None,
                'product': None,
                'bamount': None,
                'error': True,
                'message': "수량을 제대로 입력해 주세요."
            }
            return render(request, 'k99/admin/buy.html', context)


        # Buy 모델에 당일 데이터를 추가
        Buy.objects.create(
            bid = Buy.objects.order_by('-pk')[0].bid + 1,
            bamount = bamount,
            kid_id = customer.kid,
            pid_id = product.pid,
            bdate = datetime.today()
        )
    today = datetime.today()
    start_date = datetime.strptime(str(today.year) + " " + str(today.month) + " " + str(today.day), '%Y %m %d')
    end_date = datetime.strptime(str(today.year) + " " + str(today.month) + " " + str(today.day) + " 23:59", '%Y %m %d %H:%M')
    try:
        todaybuy = Buy.objects.filter(bdate__range=[start_date, end_date]) #오늘 하루의 데이터 가져옴
    except :
        context = {
            'todaybuy' : None,
            'customer': None,
            'product': None,
            'bamount': None,
            'error': True,
            'message': "오늘 조회된 상품이 없습니다."
        }

    if request.method == 'POST':
        # 모두 진행될 시 Context에 넣고 진행
        context ={
            'todaybuy' : todaybuy,
            'customer' : customer,
            'product' : product,
            'bamount' : bamount,
            'error' : False,
            'message' : None
        }
    else:
        # 모두 진행될 시 Context에 넣고 진행
        context = {
            'todaybuy': todaybuy,
            'customer': None,
            'product': None,
            'bamount': None,
            'error': False,
            'message': None
        }

    return render(request, 'k99/admin/buy.html', context)

@login_required(login_url='common:login')
def excel_export(request):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    tomorrow = datetime.today() + timedelta(days=1)
    tomorrowfilter = tomorrow.strftime('%Y-%m-%d')
    today = datetime.today().strftime('%Y%m%d')

    title = f'{today} 주문 일지'
    today = datetime.today()
    worksheet.set_column('A:L', 12)
    # worksheet.set_row(0, 57)  # 행 너비 조절
    # # 타이틀 스타일 설정
    # merge_format = workbook.add_format({
    #     'bold': 1,
    #     'border': 1,
    #     'align': 'center',
    #     'valign': 'vcenter'})
    # worksheet.merge_range('A1:G1', title, merge_format)  # 행 합치기

    # 헤더 생성
    row_num = 0
    col_names = ['K번호', '우편번호', '도착영업소', '받는분', '전화번호', '기타전화번호', '주소', '상세주소', '품목명', '수량', '제품명', '포장(kg)']


    # 헤더 스타일 설정
    header_format = workbook.add_format()
    # header_format.set_bg_color('#D9E1F2')

    # 헤더 데이터 삽입
    for idx, col_name in enumerate(col_names):
        worksheet.write(row_num, idx, col_name, header_format)
    # 내용 데이터 생성
    start_date = datetime.strptime(str(today.year) + " " + str(today.month) + " " + str(today.day), '%Y %m %d')
    end_date = datetime.strptime(str(today.year) + " " + str(today.month) + " " + str(today.day) + " 23:59",
                                 '%Y %m %d %H:%M')
    todaybuy = Buy.objects.filter(bdate__range=[start_date, end_date]).values_list('kid_id', 'pid_id','bamount')  # 오늘 하루의 데이터 가져옴
    data = []
    for tb in todaybuy:
        # K번호
        tmp = []
        tmp.append(tb[0])
        customer = Customer.objects.get(kid = tb[0])
        # 우편번호
        zc = customer.zipcode
        tmp.append(zc.rjust(5, '0'))
        # 도착영업소(공란)
        tmp.append(None)
        # 받는분
        tmp.append(customer.kname)
        # 전화번호
        tmp.append(customer.cphone)
        # 기타전화번호(공란)
        tmp.append(None)
        # 주소
        address = str(customer.doe) + ' ' + str(customer.sigungu) + ' ' + str(customer.dong) + ' '
        address = address.replace('None', '')
        tmp.append(address)
        # 상세주소
        address_sangse = str(customer.sangse) + ' ' + str(customer.sname)
        address_sangse = address_sangse.replace('None', '')
        tmp.append(address_sangse)
        # 품목명 - 세제로 고정
        tmp.append('세제')
        # 수량 20 이하는 무조건 1개, 이후 20개마다 1씩 증가
        kg = tb[2]
        if kg <= 20:
            num = 1
        else:
            num = 1
            kg -= 20
            while kg > 0:
                num += 1
                kg -= 20
        tmp.append(num)
        # 제품명
        pname = Product.objects.get(pid=tb[1]).pname
        tmp.append(pname)
        # 포장(kg)
        tmp.append(tb[2])
        #### tmp 튜플 전체를 추가
        data.append(tmp)

    # 내용 데이터 삽입
    for row_num, columns in enumerate(data):
        for col_num, cell_data in enumerate(columns):
            worksheet.write(row_num + 1, col_num, cell_data)
            worksheet.write(row_num + 1, 5, '')
            worksheet.set_column('A:A', 5)
            worksheet.set_column('B:B', 8.3)
            worksheet.set_column('C:C', 17)
            worksheet.set_column('D:D', 8.3)
            worksheet.set_column('E:E', 13.7)
            worksheet.set_column('F:F', 17.8)
            worksheet.set_column('G:G', 37.7)
            worksheet.set_column('H:H', 54.8)
            worksheet.set_column('I:I', 10.7)
            worksheet.set_column('J:J', 10.7)

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    today = datetime.today().strftime('%Y%m%d')
    filename = '주문일지_' + today + '.xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(
        quote(filename.encode('utf-8')))  # 한글 제목 설정

    return response


@login_required(login_url='common:login')
def mix(request):
    username = request.user.username
    user = Customer.objects.get(username=username)
    kid = user.kid
    regular = user.regular
    if request.method == 'GET':
        if regular:
            return render(request, 'k99/1혼합세탁.html', {'username': username})
        else:
            user_log = Searchlog.objects.filter(kid=kid, finish=True)
            user_count = user_log.count()
            if user_count >= 3:
                return render(request, 'k99/0회원가입안내.html', {'username': username})
            else:
                return render(request, 'k99/1혼합세탁.html', {'username': username})
    elif request.method == 'POST':
        ### SAVE: Next button in 'mix'
        if 'next' in request.POST:
            log = Searchlog(kid=kid, mix=makeBool(request.POST.get('mix')), mix_white=makeBool(request.POST.get('mix_white')), date=timezone.now(), stage='mix')
            log.save()
            return redirect('k99:clothes')
        ### SAVE: Search button in 'mix'
        elif 'mid-search' in request.POST:
            log = Searchlog(kid=kid, mix=makeBool(request.POST.get('mix')), mix_white=makeBool(request.POST.get('mix_white')), date=timezone.now(), stage='mix')
            log.save()
            return redirect('k99:recipe')
        ### Prev button in 'clothes'
        elif 'prev' in request.POST:
            sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
            log = get_object_or_404(Searchlog, pk=sid)
            log.delete()
            return render(request, 'k99/1혼합세탁.html', {'username': username})
        else:
            return redirect('k99:main')

@login_required(login_url='common:login')
def clothes(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
    log = get_object_or_404(Searchlog, pk=sid)
    if request.method == 'GET':
        count = getSearchCount('mix', log)
        count['username'] = username
        if log.mix:
            return render(request, 'k99/2세탁물 종류(중복).html', count)
        else:
            return render(request, 'k99/2세탁물 종류.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'clothes'
        if 'next' in request.POST:
            log.clothes = request.POST.getlist('type')
            log.stage = 'clothes'
            log.save()
            if log.mix:
                return redirect('k99:issue')
            else:
                if log.clothes[0] == '가방':
                    return redirect('k99:color')
                else:
                    return redirect('k99:material')
        ### SAVE: Search button in 'clothes'
        elif 'mid-search' in request.POST:
            log.clothes = request.POST.getlist('type')
            log.stage = 'clothes'
            log.save()
            return redirect('k99:recipe')
        ### Prev button in 'material' or 'issue'
        elif 'prev_m' in request.POST:
            count = getSearchCount('mix', log)
            count['username'] = username
            return render(request, 'k99/2세탁물 종류.html', count)
        elif 'prev' in request.POST:
            count = getSearchCount('mix', log)
            count['username'] = username
            return render(request, 'k99/2세탁물 종류(중복).html', count)
        else:
            return redirect('k99:main')

@login_required(login_url='common:login')
def material(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
    log = get_object_or_404(Searchlog, pk=sid)
    if request.method == 'GET':
        count = getSearchCount('clothes', log)
        count['username'] = username
        if log.clothes[2:-2] == '신발':
            return render(request, 'k99/3.1신발.html', count)
        else:
            return render(request, 'k99/3소재.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'material'
        if 'next' in request.POST:
            log.material = request.POST.getlist('material')
            log.stage = 'material'
            log.save()
            return redirect('k99:color')
        ### SAVE: Search button in 'material'
        elif 'mid-search' in request.POST:
            log.material = request.POST.getlist('material')
            log.stage = 'material'
            log.save()
            return redirect('k99:recipe')
        ### Prev button in 'color'
        elif log.clothes[2:-2] == '신발':
            count = getSearchCount('clothes', log)
            count['username'] = username
            return render(request, 'k99/3.1신발.html', count)
        else:
            count = getSearchCount('clothes', log)
            count['username'] = username
            return render(request, 'k99/3소재.html', count)

@login_required(login_url='common:login')
def color(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
    log = get_object_or_404(Searchlog, pk=sid)
    if request.method == 'GET':
        if log.clothes[2:-2] == '가방':
            count = getSearchCount('clothes', log)
            count['username'] = username
            return render(request, 'k99/4.1색상.html', count)
        else:
            count = getSearchCount('material', log)
            count['username'] = username
            return render(request, 'k99/4색상.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'color'
        if 'next' in request.POST:
            log.color = request.POST.getlist('color')
            log.stage = 'color'
            log.save()
            return redirect('k99:issue')
        ### SAVE: Search button in 'color'
        elif 'mid-search' in request.POST:
            log.color = request.POST.getlist('color')
            log.stage = 'color'
            log.save()
            return redirect('k99:recipe')
        ### Prev button in 'issue'
        elif log.clothes[2:-2] == '가방':
            count = getSearchCount('clothes', log)
            count['username'] = username
            return render(request, 'k99/4.1색상.html', count)
        else:
            count = getSearchCount('material', log)
            count['username'] = username
            return render(request, 'k99/4색상.html', count)

@login_required(login_url='common:login')
def issue(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
    log = get_object_or_404(Searchlog, pk=sid)
    if request.method == 'GET':
        if log.mix:
            count = getSearchCount('clothes', log)
            data = {
                'data': True, # 2
                'count': count['count'],
                'username': username,
            }
            return render(request, 'k99/5세탁 사유.html', data)
        else:
            count = getSearchCount('color', log)
            data = {
                'data': False, # 4
                'count': count['count'],
                'username': username,
            }
            return render(request, 'k99/5세탁 사유.html', data)
    elif request.method == 'POST':
        ### SAVE: Next button in 'issue'
        if 'next' in request.POST:
            log.issue = request.POST.getlist('reason')
            log.issue_detail = [request.POST.getlist('유색오염'), request.POST.getlist('생활얼룩'), request.POST.getlist('기타')]
            log.stage = 'issue'
            log.save()
            return redirect('k99:luxury')
        ### SAVE: Search button in 'issue'
        elif 'mid-search' in request.POST:
            log.issue = request.POST.getlist('reason')
            log.issue_detail = [request.POST.getlist('유색오염'), request.POST.getlist('생활얼룩'), request.POST.getlist('기타')]
            log.stage = 'issue'
            log.save()
            return redirect('k99:recipe')
        ### Prev button in 'luxury'
        elif 'prev' in request.POST:
            if log.mix:
                count = getSearchCount('clothes', log)
                data = {
                    'data': True,  # 2
                    'count': count['count'],
                    'username': username,
                }
                return render(request, 'k99/5세탁 사유.html', data)
            else:
                count = getSearchCount('color', log)
                data = {
                    'data': False,  # 4
                    'count': count['count'],
                    'username': username,
                }
                return render(request, 'k99/5세탁 사유.html', data)
        else:
            return redirect('k99:main')

@login_required(login_url='common:login')
def luxury(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
    log = get_object_or_404(Searchlog, pk=sid)
    if request.method == 'GET':
        count = getSearchCount('issue', log)
        count['username'] = username
        return render(request, 'k99/6명품.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'luxury'
        log.luxury = makeBool(request.POST.get('named'))
        log.stage = 'luxury'
        log.save()
        return redirect('k99:recipe')


@login_required(login_url='common:login')
def recipe(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
    log = get_object_or_404(Searchlog, pk=sid)
    if request.method == 'GET':
        count = getSearchCount(log.stage, log)
        log.finish = True
        log.save()
        page = request.GET.get('page', '1')
        tmp_post_list = count['pid']
        #tmp_post_list = Posts.objects.all()
        post_list = REpostObjRevision(tmp_post_list)
        paginator = Paginator(post_list, 10)
        page_obj = paginator.get_page(page)
        context = {
            'post_list': page_obj,
            'count': count['count'],
            'username': username,
        }
        return render(request, 'k99/실전사례.html', context)


@login_required(login_url='common:login')
def qna(request):
    username = request.user.username
    user = Customer.objects.get(username=username)
    kid = user.kid
    regular = user.regular
    if request.method == 'GET':
        if regular:
            return render(request, 'k99/질문답변.html', {'username': username})
        else:
            user_log = Searchlog.objects.filter(kid=kid, finish=True)
            user_count = user_log.count()
            if user_count >= 3:
                return render(request, 'k99/0회원가입안내.html', {'username': username})
            else:
                return render(request, 'k99/질문답변.html', {'username': username})


@login_required(login_url='common:login')
def qnaCategory(request):
    username = request.user.username
    page = request.GET.get('page', '1')
    ctgry = request.GET.get('ctgry')
    # print(ctgry)
    ### 세탁방법
    if ('recipe' in request.POST) or (ctgry == 'recipe'):
        category = 'recipe'
        count = getQACount('recipe')
        tmp_post_list = count['pid_nprof']
        prof_list = count['pid_prof']
    ### 세탁약품
    elif ('chemical' in request.POST) or (ctgry == 'chemical'):
        category = 'chemical'
        count = getQACount('chemical')
        tmp_post_list = count['pid_nprof']
        prof_list = count['pid_prof']
    ### 도구사용법
    elif ('tool' in request.POST) or (ctgry == 'tool'):
        category = 'tool'
        count = getQACount('tool')
        tmp_post_list = count['pid_nprof']
        prof_list = count['pid_prof']
    ### 문제발생원인
    elif ('problem' in request.POST) or (ctgry == 'problem'):
        category = 'problem'
        count = getQACount('problem')
        tmp_post_list = count['pid_nprof']
        prof_list = count['pid_prof']
    ### 기타
    elif ('etc' in request.POST) or (ctgry == 'etc'):
        category = 'etc'
        count = getQACount('etc')
        tmp_post_list = count['pid_nprof']
        prof_list = count['pid_prof']
    post_list = QApostObjRevision(tmp_post_list, prof_list)
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page)
    context = {
        'post_list': page_obj,
        'count': len(post_list),
        'ctgry': category,
        'username': username,
    }
    return render(request, 'k99/질문답변_카테고리.html', context)


@login_required(login_url='common:login')
def detail(request, qna_id):
    username = request.user.username
    obj = get_object_or_404(Posts, pk=qna_id)
    subject = QnA.objects.get(pid_id=qna_id).subject
    pvurl = listOrNone(obj.pvurl)
    post = [obj, pvurl, subject]
    context = {
        'post': post,
        'username': username,
    }
    return render(request, 'k99/질문답변_detail.html', context)

@login_required(login_url='common:login')
def adding(request):
    context = {}
    return render(request, 'k99/admin/adding.html', context)

@login_required(login_url="common:login")
def realexamplemanage(request):
    context = {}
    return render(request, 'k99/admin/manangerealexample.html', context)

@login_required(login_url="common:login")
def realexampleadd(request):
    context = {}
    return render(request, 'k99/admin/addingrealexample.html', context)

@login_required(login_url="common:login")
def addpost(request):
    try:
        pvurl = request.POST.get("pvurlinput")
        pvurls = pvurl.replace(" ", "").split(",")
        Posts.objects.create(
            pid=request.POST.get("pidinput"),
            create_date = request.POST.get("create_dateinput"),
            content = request.POST.get("contentinput"),
            tag ="#실전사례",
            pvurl = pvurls,
            kid_id = request.POST.get("kidinput")
        )
        context = {"error" : False,
                   "message" : None,
                   "pid" : request.POST.get("pidinput")}
    except Exception as e:
        context = {"error" : True,
                   "message" : "이미 등록된 포스트거나 존재하지 않는 k번호입니다.",
                   "pid" : None}
    return render(request, 'k99/admin/addrealexample.html', context)

@login_required(login_url="common:login")
def addrealexample(request):
    # id
    add_id = Realexamples.objects.order_by('-pk')[0].id + 1
    # 소재
    add_material = listClean(request.POST.getlist('material'))
    # 혼합세탁 여부
    add_mix = makeBoolFromYN(request.POST.get('mix'))
    if add_mix:
        add_mix_white = makeBoolFromYN(listClean(["yes" if request.POST.get('흰색유무')=="white" else "no"]))
    else:
        add_mix_white = None
    # 세탁사유
    add_reason = listClean(request.POST.getlist('reason'))
    # 세탁세부사유 - 유색오염
    tmp = []
    if "유색오염" in request.POST.keys():
        try:
            tmp.append(listClean(request.POST.getlist("유색오염")))
        except:
            tmp.append("없음")
    if "생활얼룩" in request.POST.keys():
        try:
            tmp.append(listClean(request.POST.getlist("생활얼룩")))
        except:
            tmp.append("없음")
    if "기타" in request.POST.keys():
        try:
            tmp.append(listClean(request.POST.getlist("기타")))
        except:
            tmp.append("없음")
    if tmp:
        add_issue_detail = listClean(tmp)
    else:
        add_issue_detail = None
    # 유색
    if "유색" in request.POST.getlist('reason'):
        add_color =  "유색"
    elif "흰색" in request.POST.getlist('reason'):
        add_color = "흰색"
    else:
        add_color = "유색"
    # 배색, 프린팅
    if "배색" in request.POST.getlist('reason'):
        add_comb_colors = True
    else:
        add_comb_colors = False
    if "프린팅" in request.POST.getlist('reason'):
        add_printing = True
    else:
        add_printing = False
    # 옷종류
    add_type = listClean(request.POST.getlist('type'))
    # 명품
    add_named = makeBoolFromYN(request.POST.get('named'))
    # post id
    add_pid_id = request.POST.get('pid')
    Realexamples.objects.create(
        id = add_id,
        material_out = add_material,
        material_in = "없음",
        issue = add_reason,
        issue_detail = add_issue_detail,
        color = add_color,
        comb_colors = add_comb_colors,
        printing = add_printing,
        clothes = add_type,
        luxury = add_named,
        mix = add_mix,
        mix_white = add_mix_white,
        pid_id = add_pid_id
    )
    context = {}
    return render(request, 'k99/admin/addingrealexample.html', context)
# qna


@login_required(login_url="common:login")
def qnamanage(request):
    context = {}
    return render(request, 'k99/admin/manageqna.html', context)

@login_required(login_url="common:login")
def qnaadd(request):
    context = {}
    return render(request, 'k99/admin/addingqna.html', context)

@login_required(login_url="common:login")
def addpost_qna(request):
    try:
        pvurl = request.POST.get("pvurlinput")
        pvurls = pvurl.replace(" ", "").split(",")
        Posts.objects.create(
            pid=request.POST.get("pidinput"),
            create_date = request.POST.get("create_dateinput"),
            content = request.POST.get("contentinput"),
            tag ="#질문답변",
            pvurl = pvurls,
            kid_id = request.POST.get("kidinput")
        )
        context = {"error" : False,
                   "message" : None,
                   "pid" : request.POST.get("pidinput")}
    except Exception as e:
        context = {"error" : True,
                   "message" : "이미 등록된 포스트거나 존재하지 않는 k번호입니다.",
                   "pid" : None}
    return render(request, 'k99/admin/addqna.html', context)

def addqna(request):
    # id
    add_id = QnA.objects.order_by('-pk')[0].id + 1
    # 카테고리
    add_category = request.POST.get('category')
    # 제목
    add_subject = request.POST.get('subjectinput')
    # 교수님 답변 여부
    add_prof = makeBoolFromYN(request.POST.get('prof'))
    # pid
    add_pid_id = request.POST.get('pid')
    QnA.objects.create(
        id = add_id,
        category = add_category,
        subject = add_subject,
        prof = add_prof,
        pid_id = add_pid_id
    )
    context = {}
    return render(request, 'k99/admin/addingqna.html', context)

@login_required(login_url='common:login')
def log_export(request):
    # Create an in-memory output file for the new workbook.
    output = io.BytesIO()

    workbook = xlsxwriter.Workbook(output)
    worksheet = workbook.add_worksheet()
    today = datetime.today().strftime('%Y%m%d')

    title = f'검색로그(~{today})'
    today = datetime.today()
    worksheet.set_column('A:N', 12)
    worksheet.set_row(0, 57)  # 행 너비 조절
    # 타이틀 스타일 설정
    merge_format = workbook.add_format({
        'bold': 1,
        'border': 1,
        'align': 'center',
        'valign': 'vcenter'})
    worksheet.merge_range('A1:N1', title, merge_format)  # 행 합치기

    # 헤더 생성
    row_num = 1
    col_names = ['검색id', 'K번호', '이름', '검색일시', '혼합세탁여부', '혼합세탁_흰색포함여부',
                 '세탁물종류', '소재', '세탁사유', '세탁세부사유', '유색/무색', '배색여부', '프린팅여부', '명품여부']

    # 헤더 스타일 설정
    header_format = workbook.add_format()
    header_format.set_bg_color('#D9E1F2')

    # 헤더 데이터 삽입
    for idx, col_name in enumerate(col_names):
        worksheet.write(row_num, idx, col_name, header_format)

    date_format = workbook.add_format({'num_format': 'yyyy-mm-dd hh:mm:ss AM/PM'})
    # 내용 데이터 생성
    allsearchlog = Searchlog.objects.all()
    data = []
    for searchlog in allsearchlog:
        tmp = []
        # sid
        tmp.append(searchlog.sid)
        # kid
        kid = searchlog.kid
        tmp.append(kid)
        # kname
        kname = Customer.objects.get(kid=kid).kname
        tmp.append(kname)
        # date
        # t = searchlog.date.replace(tzinfo=None)
        tmp.append(searchlog.date)
        # mix
        tmp.append(searchlog.mix)
        # mix_whites
        tmp.append(searchlog.mix_white)
        # clothes
        tmp.append(listClean(searchlog.clothes))
        # material
        tmp.append(listClean(searchlog.material))
        # issue
        tmp.append(listClean(searchlog.issue))
        # issue_detail
        tmp.append(listClean(searchlog.issue_detail))
        colors = listClean(searchlog.color)
        # clorol
        if "유색" in colors:
            tmp.append("유색")
        elif "흰색" in colors:
            tmp.append("흰색")
        else:
            tmp.append("None")
        # comb_color
        if "배색" in colors:
            tmp.append(True)
        else:
            tmp.append(False)
        # printing
        if "프린팅" in colors:
            tmp.append(True)
        else:
            tmp.append(False)
        # luxury
        tmp.append(searchlog.luxury)

        #### tmp 튜플 전체를 추가
        data.append(tmp)

    # 내용 데이터 삽입
    for row_num, columns in enumerate(data):
        for col_num, cell_data in enumerate(columns):
            if col_num != 3:
                worksheet.write(row_num + 2, col_num, cell_data)
            else:
                worksheet.write_datetime(row_num + 2, col_num, cell_data, date_format)
            worksheet.write(row_num + 2, 5, '')
            worksheet.set_column('A:A', 8)
            worksheet.set_column('B:B', 8)
            worksheet.set_column('C:C', 8.3)
            worksheet.set_column('D:D', 25, date_format)
            worksheet.set_column('E:E', 8)
            worksheet.set_column('F:F', 8)
            worksheet.set_column('G:G', 25)
            worksheet.set_column('H:H', 20)
            worksheet.set_column('I:I', 25)
            worksheet.set_column('J:J', 25)

    # Close the workbook before sending the data.
    workbook.close()

    # Rewind the buffer.
    output.seek(0)

    # Set up the Http response.
    today = datetime.today().strftime('%Y%m%d')
    filename = f'검색로그(~{today}).xlsx'
    response = HttpResponse(
        output,
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = "attachment; filename*=UTF-8''{}".format(
        quote(filename.encode('utf-8')))  # 한글 제목 설정

    return response