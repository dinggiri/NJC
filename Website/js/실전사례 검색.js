$(function (){
    $('input[type="radio"][name="mix"]').on('click', function(){
        var chkValue = $('input[type=radio][name="mix"]:checked').val();
        if(chkValue == 'yes'){
            $('#details_item').css('display','block');
        }else if(chkValue == 'no'){
            $('#details_item').css('display','none');
        }
    });
    });
     