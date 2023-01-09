$(function (){
    $('input[type="radio"][name="mix"]').on('click', function(){
        var chkValue = $('input[type=radio][name="mix"]:checked').val();
        if(chkValue == 'yes'){
            $('#white_item').css('display','block');
        }else{
            $('#white_item').css('display','none');
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
    $('input[type="reset"][name="init"]').on('click', function(){
        $('#white_item').css('display','none');
        $('#col_reason_item').css('display','none');
        $('#blemish_item').css('display','none');
        $('#etc_item').css('display','none');
    });
});
     