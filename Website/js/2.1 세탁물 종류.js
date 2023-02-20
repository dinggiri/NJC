$(function (){
    $('.mid-search').on('click', function(){
        var chkLength = $('input[type=radio][name="type"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
            return false;
        }
    });
    $('.next').on('click', function(){
        var chkLength = $('input[type=radio][name="type"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
            return false;
        }
    });
});