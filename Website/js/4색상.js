$(function (){
    $('.next').on('click', function(){
        var chkLength = $('input[type=radio][name="color"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
        }
    });
    $('.next').on('click', function(){
        var chkLength2 = $('input[type=checkbox][name="color"]:checked').length;
        if(chkLength2 < 1){
            alert("하나 이상 체크해주세요");
        }
    });
});