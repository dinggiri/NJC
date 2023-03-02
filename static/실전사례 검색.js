$(function (){
    $('input[type="radio"][name="addmix"]').on('click', function(){
        var chkValue = $('input[type=radio][name="addmix"]:checked').val();
        if(chkValue == 'yes'){
            $('#addwhite_item').css('display','block');
        }else{
            $('#addwhite_item').css('display','none');
        }
    });
    $('input[type="checkbox"][name="addreason"][value="유색오염"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="addreason"][value="유색오염"]:checked').val();
        if(chkValue == '유색오염'){
            $('#addcol_reason_item').css('display','block');
        }else{$('#addcol_reason_item').css('display','none');
        }
    });
    $('input[type="checkbox"][name="addreason"][value="생활얼룩"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="addreason"][value="생활얼룩"]:checked').val();
        if(chkValue == '생활얼룩'){
            $('#addblemish_item').css('display','block');
        }else{$('#addblemish_item').css('display','none');
        }
    });
    $('input[type="checkbox"][name="addreason"][value="기타"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="addreason"][value="기타"]:checked').val();
        if(chkValue == '기타'){
            $('#addetc_item').css('display','block');
        }else{$('#addetc_item').css('display','none');
        }
    });
    $('input[type="reset"][name="init"]').on('click', function(){
        $('#white_item').css('display','none');
        $('#col_reason_item').css('display','none');
        $('#blemish_item').css('display','none');
        $('#etc_item').css('display','none');
    });
});
     