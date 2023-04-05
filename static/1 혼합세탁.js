$(function (){
    $('.move').on('click', function(){
        var chkLength = $('input[type=radio][name="mix_white"]:checked').length;
        if(chkLength < 1){
            alert("흰색 포함 여부를 체크해주세요");
            return false;
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