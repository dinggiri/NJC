$(function (){
    $('input[type="radio"][name="mix"]').on('click', function(){
        var chkValue = $('input[type=radio][name="mix"]:checked').val();
        if(chkValue == 'true'){
            $('#white_item').css('display','block');
        }else{
            $('#white_item').css('display','none');
        }
    });
    $('.next').on('click', function(){
        var chkLength = $('input[type=radio][name="mix"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
            return false;
        }
    });
    $('.next').on('click', function(){
        var chkLength = $('input[type=radio][name="mix"]:checked').length;
        var chkValue = $('input[type=radio][name="mix"]:checked').val();
        var chkLength2 = $('input[type=radio][name="mix_white"]:checked').length;
        if((chkLength == 1) & (chkValue == 'true')){
            if(chkLength2 < 1){
                alert("하나 이상 체크해주세요");
                return false;
            }
        }
    });
});
