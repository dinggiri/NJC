$(function (){
    $('.mid-search').on('click', function(){
        var chkMLength = $('input[type=checkbox][name="material"]:checked').length;
        var chkCLength = $('input[type=radio][name="type"]:checked').length;
        if(chkMLength < 1 & chkCLength < 1){
            alert("소재와 세탁물 종류를 체크해주세요");
            return false;
        }
        else if(chkMLength < 1){
            alert("소재를 하나 이상 체크해주세요");
            return false;
        }
        else if(chkCLength < 1){
            alert("세탁물 종류를 체크해주세요");
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