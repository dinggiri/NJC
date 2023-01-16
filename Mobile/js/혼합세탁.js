$(function (){
    $('input[type="radio"][name="mix"]').on('click', function(){
        var chkValue = $('input[type=radio][name="mix"]:checked').val();
        if(chkValue == 'yes'){
            $('#white_item').css('display','block');
        }else{
            $('#white_item').css('display','none');
        }
    });
});