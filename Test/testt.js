
$(document).ready(function() {
    $('input[type=checkbox][name=type][value=신발]').change(function() {
        var chkValue = $('input[type=checkbox][name="type"]:checked').val();
        var chkLength = $('input[type=checkbox][name="type"]:checked').length;
        if (chkLength == 1) {
            if (chkValue='신발') {
                $('.next').attr('onclick',"location.href='3.1신발.html'");
            }
            else {
                $('.next').attr('onclick',"location.href='3소재.html'");
            }
        }
        else {
            $('.next').attr('onclick',"location.href='3소재.html'");
        }
    });
});



//체크박스 중 체크된 체크박스만 가져와서 Loop 합니다.
$(document).ready(function() {
    $('input[type=checkbox][name="type"]:checked').each(function(i,elements){
        //해당 index(순서)값을 가져옵니다.
        index = $(elements).index("'input[type=checkbox][name=type]");
        shoesIndex = $(elements).index("'input[type=checkbox][name=type][value=신발]");
        //해당 index에 해당하는 체크박스의 값을 가져옵니다.
        alert($("input[type=checkbox][name=type]").eq(index),val());
        if (shoesIndex == 0) {
            $('.next').attr('onclick',"location.href='3.1신발.html'");
        }
        else {
            $('.next').attr('onclick',"location.href='3소재.html'");
        }
    });
});
