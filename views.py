from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Customer, CustomerManager, Searchlog, Realexamples, Posts
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login
import ast
import pandas as pd

def makeBool(str):
    if str is None:
        return str
    elif str.lower() == 'true':
        return True
    elif str.lower() == 'false':
        return False
    else:
        return str

def listOrNone(var):
    if type(var) == list:
        return var
    elif var is not None:
        return ast.literal_eval(var)
    else:
        return None

def postObjRevision(obj):
    postObj = []
    for post in obj:
        ### 나중에 kname --> 밴드 닉네임(author_name)으로 바꾸기(DB 수정 필요)
        if post.kid_id is None:
            kname = None
        else:
            kname = Customer.objects.get(kid=post.kid_id).kname
        pvurl = listOrNone(post.pvurl)
        postObj.append([post, kname, pvurl])
    return postObj

def _getSearchCount(results, criterion):
    if type(results) == pd.core.frame.DataFrame:
        total_df = results.sort_values(by=['score'], ascending=False)
        ### Set minimum(10)
        if len(total_df) > 10:
            # 역치? 설정
            df = total_df[total_df.score >= criterion]
            if len(df) <= 10:
                df = total_df
        else:
            df = total_df
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
    criterion_1 = [1000, 70, 40, 20, 0]      # clothes
    criterion_2 = [2000, 140, 100, 70, 0]    # material
    criterion_3 = [3000, 220, 160, 100, 0]   # issue
    criterion_4 = [500, 0]                   # issue_detail
    criterion_5 = [10000, 0]                # luxury


    ### 1. 혼합세탁
    mix = log.mix
    mix_white = log.mix_white
    results = Realexamples.objects.filter(mix=mix, mix_white=mix_white)
    if stage == 'mix':
        criterion = 0 # 필요없음
        return _getSearchCount(results, criterion)


    ### 2. 세탁물종류
    clothes = listOrNone(log.clothes)
    df = pd.DataFrame(list(results.values()))
    df.insert(df.shape[1], 'score', 0)

    def _Clothes(item):
        score = 0
        dct = {'상의': [], '하의': [], '원피스': [], '겉옷': [], '패딩': [], '가방': [], '신발': [], '모자': [], '한복': [], '침구류': [], '기타': []}
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
                if '원피스' in item: score += criterion_1[2]
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

    if stage == 'clothes':
        criterion = criterion_1[0]  # 1000
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
                   '아크릴': [], '아세테이트': [], '모피': [], '스웨이드': [], '동물털': [], '인조가죽': [], '폴리우레탄': [], '솜': [], '기타': [], '모름': []}
            for m in material:
                if m in item:
                    dct[m].append(criterion_2[0])
                if '모름' in item:
                    dct['모름'].append(criterion_2[3])

            for it, scores in dct.items():
                if len(dct[it]) != 0:
                    score += max(dct[it])
            return score

        df['score'] += df['material'].apply(_Material)

        if stage == 'material':
            criterion = criterion_2[0]  # 2000
            return _getSearchCount(df, criterion)


    ### 4. 색상
    if not mix:
        total_color = listOrNone(log.color)
        color = total_color[0]
        if '배색' in total_color: comb_colors = True
        else: comb_colors = False
        if '프린팅' in total_color: printing = True
        else: printing = False

        df['score'] += df['color'].apply(lambda x: criterion_1[0] if x == color else criterion_1[4])
        df['score'] += df['comb_colors'].apply(lambda x: criterion_1[0] if x == comb_colors else criterion_1[2])
        df['score'] += df['printing'].apply(lambda x: criterion_1[0] if x == printing else criterion_1[2])

        if stage == 'color':
            criterion = criterion_1[0] + criterion_2[0]  # 3000
            return _getSearchCount(df, criterion)


    ### 5. 세탁사유
    issue = listOrNone(log.issue)
    issue_detail = listOrNone(log.issue_detail)  # [[유색오염],[생활얼룩],[기타]]

    def _Issue(item):
        score = 0
        dct = {'이염': [], '유색오염': [], '음식물': [], '황변': [], '곰팡이': [], '기름': [], '생활얼룩': [], '변색': [], '기타': [], '모름': [], '없음': []}
        for i in issue:
            if i in item:
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
        for iss in issue_detail:
            for d in iss:
                if d in item:
                    dct[d].append(criterion_4[0])

        for it, scores in dct.items():
            if len(dct[it]) != 0:
                score += max(dct[it])
        return score

    df['score'] += df['issue'].apply(_Issue)
    df['score'] += df['issue_detail'].apply(_IssueDetail)

    if stage == 'issue':
        criterion = criterion_1[0] + criterion_2[0] + criterion_3[0]  # 6000
        return _getSearchCount(df, criterion)


    ### 6. 명품
    luxury = log.luxury
    df['score'] += df['luxury'].apply(lambda x: criterion_5[0] if x == luxury else criterion_5[1])

    if stage == 'luxury':
        criterion = criterion_5[0]  # 10000
        return _getSearchCount(df, criterion)



@login_required(login_url='common:login')
def main(request):
    username = request.user.username
    if username == 'admin':
        return render(request, 'k99/admin/main.html')
        #return render(request, 'k99/main.html')
    else:
        return render(request, 'k99/main.html')

def customer(request):
    if request.method == "GET":
        return render(request, 'k99/admin/customer.html')
    elif request.method == "POST":
        ### CREATE: Create button in 'customer'
        if 'create' in request.POST:
            username = request.POST.get('IDinput')
            password = request.POST.get('PWinput')
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
            regular = makeBool(request.POST.get('regularinput'))
            cphone = request.POST.get('cphoneinput')
            email = 0
            a = CustomerManager()
            a.create_customer(username=username, password=password, kname=kname, kid=kid, doe=doe, sigungu=sigungu,
                                            dong=dong,sangse=sangse, sname=sname, note=note, zipcode=zipcode, cdate=cdate,
                                            regular=regular, cphone=cphone, email=email)
            return render(request, 'k99/admin/main.html')

def Recipe(request, count):
    print(count['count'])
    page = request.GET.get('page', '1')
    # tmp_post_list = count['pid']
    tmp_post_list = Posts.objects.all()
    post_list = postObjRevision(tmp_post_list)
    paginator = Paginator(post_list, 10)
    page_obj = paginator.get_page(page)
    context = {
        'post_list': page_obj,
        'count': count['count'],
    }
    return render(request, 'k99/실전사례.html', context)


@login_required(login_url='common:login')
def mix(request):
    username = request.user.username
    kid = Customer.objects.get(username=username).kid
    if request.method == 'GET':
        return render(request, 'k99/1혼합세탁.html')
    elif request.method == 'POST':
        ### SAVE: Next button in 'mix'
        if 'next' in request.POST:
            log = Searchlog(kid=kid, mix=makeBool(request.POST.get('mix')), mix_white=makeBool(request.POST.get('mix_white')), date=timezone.now())
            log.save()
            return redirect('k99:clothes')
        ### SAVE: Search button in 'mix'
        elif 'mid-search' in request.POST:
            log = Searchlog(kid=kid, mix=makeBool(request.POST.get('mix')), mix_white=makeBool(request.POST.get('mix_white')), date=timezone.now())
            count = getSearchCount('mix', log)
            log.save()
            return Recipe(request, count)
        ### Prev button in 'clothes'
        elif 'prev' in request.POST:
            sid = Searchlog.objects.filter(kid=kid).latest('sid').sid
            log = get_object_or_404(Searchlog, pk=sid)
            log.delete()
            return render(request, 'k99/1혼합세탁.html')
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
        if log.mix:
            return render(request, 'k99/2세탁물 종류(중복).html', count)
        else:
            return render(request, 'k99/2세탁물 종류.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'clothes'
        if 'next' in request.POST:
            log.clothes = request.POST.getlist('type')
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
            count = getSearchCount('clothes', log)
            log.save()
            return Recipe(request, count)
        ### Prev button in 'material' or 'issue'
        elif 'prev_m' in request.POST:
            count = getSearchCount('mix', log)
            return render(request, 'k99/2세탁물 종류.html', count)
        elif 'prev' in request.POST:
            count = getSearchCount('mix', log)
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
        if log.clothes[2:-2] == '신발':
            return render(request, 'k99/3.1신발.html', count)
        else:
            return render(request, 'k99/3소재.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'material'
        if 'next' in request.POST:
            log.material = request.POST.getlist('material')
            log.save()
            return redirect('k99:color')
        ### SAVE: Search button in 'material'
        elif 'mid-search' in request.POST:
            log.material = request.POST.getlist('material')
            count = getSearchCount('material', log)
            log.save()
            return Recipe(request, count)
        ### Prev button in 'color'
        elif log.clothes[2:-2] == '신발':
            count = getSearchCount('clothes', log)
            return render(request, 'k99/3.1신발.html', count)
        else:
            count = getSearchCount('clothes', log)
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
            return render(request, 'k99/4.1색상.html', count)
        else:
            count = getSearchCount('material', log)
            return render(request, 'k99/4색상.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'color'
        if 'next' in request.POST:
            log.color = request.POST.getlist('color')
            log.save()
            return redirect('k99:issue')
        ### SAVE: Search button in 'color'
        elif 'mid-search' in request.POST:
            log.color = request.POST.getlist('color')
            count = getSearchCount('color', log)
            log.save()
            return Recipe(request, count)
        ### Prev button in 'issue'
        elif log.clothes[2:-2] == '가방':
            count = getSearchCount('clothes', log)
            return render(request, 'k99/4.1색상.html', count)
        else:
            count = getSearchCount('material', log)
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
            }
            return render(request, 'k99/5세탁 사유.html', data)
        else:
            count = getSearchCount('color', log)
            data = {
                'data': False, # 4
                'count': count['count'],
            }
            return render(request, 'k99/5세탁 사유.html', data)
    elif request.method == 'POST':
        ### SAVE: Next button in 'issue'
        if 'next' in request.POST:
            log.issue = request.POST.getlist('reason')
            log.issue_detail = [request.POST.getlist('유색오염'), request.POST.getlist('생활얼룩'), request.POST.getlist('기타')]
            log.save()
            return redirect('k99:luxury')
        ### SAVE: Search button in 'issue'
        elif 'mid-search' in request.POST:
            log.issue = request.POST.getlist('reason')
            log.issue_detail = [request.POST.getlist('유색오염'), request.POST.getlist('생활얼룩'), request.POST.getlist('기타')]
            count = getSearchCount('issue', log)
            log.save()
            return Recipe(request, count)
        ### Prev button in 'luxury'
        elif 'prev' in request.POST:
            if log.mix:
                count = getSearchCount('clothes', log)
                data = {
                    'data': True,  # 2
                    'count': count['count'],
                }
                return render(request, 'k99/5세탁 사유.html', data)
            else:
                count = getSearchCount('color', log)
                data = {
                    'data': False,  # 4
                    'count': count['count'],
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
        return render(request, 'k99/6명품.html', count)
    elif request.method == 'POST':
        ### SAVE: Next button in 'luxury'
        log.luxury = makeBool(request.POST.get('named'))
        count = getSearchCount('luxury', log)
        log.save()
        return Recipe(request, count)


@login_required(login_url='common:login')
def qna(request):
    if request.method == 'GET':
        return render(request, 'k99/질문답변.html')
    elif request.method == 'POST':
        page = request.GET.get('page', '1')
        if 'recipe' in request.POST:
            #tmp_post_list = QnA.objects.filter(tag='recipe')
            tmp_post_list = Posts.objects.all()
        elif 'chemical' in request.POST:
            # tmp_post_list = QnA.objects.filter(tag='chemical')
            tmp_post_list = Posts.objects.all()
        post_list = postObjRevision(tmp_post_list)
        paginator = Paginator(post_list, 10)
        page_obj = paginator.get_page(page)
        context = {
            'post_list': page_obj,
            'count': len(post_list),
        }
        return render(request, 'k99/질문답변_카테고리.html', context)


@login_required(login_url='common:login')
def detail(request, qna_id):
    #qna = get_object_or_404(QnA, pk=qna_id)
    qna = get_object_or_404(Posts, pk=qna_id)
    context = {'qna': qna}
    return render(request, 'k99/질문답변_detail.html', context)
