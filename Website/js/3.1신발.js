$(function (){
    $('.mid-search').on('click', function(){
        var chkLength = $('input[type=checkbox][name="material"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
            return false;
        }
    });
    $('.next').on('click', function(){
        var chkLength = $('input[type=checkbox][name="material"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
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
