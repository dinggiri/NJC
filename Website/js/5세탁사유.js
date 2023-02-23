$(function (){
    $('.mid-search').on('click', function(){
        var chkLength = $('input[type=checkbox][name="reason"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
            return false;
        }
    });
    $('.next').on('click', function(){
        var chkLength = $('input[type=checkbox][name="reason"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
            return false;
        }
    });
    $('input[type="checkbox"][name="reason"][value="유색오염"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="reason"][value="유색오염"]:checked').val();
        if(chkValue == '유색오염'){
            $('#col_reason_item').css('display','block');
        }else{$('#col_reason_item').css('display','none');
        }
    });
    $('input[type="checkbox"][name="reason"][value="생활얼룩"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="reason"][value="생활얼룩"]:checked').val();
        if(chkValue == '생활얼룩'){
            $('#blemish_item').css('display','block');
        }else{$('#blemish_item').css('display','none');
        }
    });
    $('input[type="checkbox"][name="reason"][value="기타"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="reason"][value="기타"]:checked').val();
        if(chkValue == '기타'){
            $('#etc_item').css('display','block');
        }else{$('#etc_item').css('display','none');
        }
    });
});

$(function (){
    $('.guide').on('click', function(){
        $('.guide_page').css('display','flex');
    });
    $('.guide_page').on('click', function(){
        $('.guide_page').css('display','none');
    });
});
