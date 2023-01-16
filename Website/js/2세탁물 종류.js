$(function (){
    $('input[type="checkbox"][name="type"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="type"]:checked').val();
        if(chkValue == '신발'){
            $('.next').attr('href','3.1신발.html');
        }
    });
    $('input[type="checkbox"][name="type"]').on('click', function(){
        var chkValue = $('input[type=checkbox][name="type"]:checked').val();
        if(chkValue == '가방'){
            $('.next').attr('href','4색상.html');
        }
    });
});



$(document).ready(function() {
    $('input[type=checkbox][name=type][value=신발]').change(function() {
        if (this.checked) {
            $('.next').attr('href','3.1신발.html');
        }
        else {
            alert(`${this.value} is unchecked`);
        }
    });
});