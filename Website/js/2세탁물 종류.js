$(function (){
    $('input[type="checkbox"][name="type"][value="가방"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="type"]:checked').val();
        if(chkValue == '가방'){
            $('.next').attr('onclick',"location.href='4.1색상.html'");
        }
        else{
            $('.next').attr('onclick',"location.href='3소재.html'");
        }
    });
    $('input[type="checkbox"][name="type"][value="신발"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="type"]:checked').val();
        if(chkValue == '신발'){
            $('.next').attr('onclick',"location.href='3.1신발.html'");
        }
        else {
            $('.next').attr('onclick',"location.href='3소재.html'");
        }
    });
    $('input[type="checkbox"][name="type"]').on('click', function(){
        var chkLength = $('input[type=checkbox][name="type"]:checked').length;
        if(chkLength > 1){
            $('.next').attr('onclick',"location.href='3소재.html'");
        }
    });
    $('.next').on('click', function(){
        var chkLength = $('input[type=checkbox][name="type"]:checked').length;
        if(chkLength < 1){
            alert("하나 이상 체크해주세요");
        }
    });
});