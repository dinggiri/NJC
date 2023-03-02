$(function (){
    $('.show_info').on('click', function(){
        $('.info_page').css('display','flex');
    });
    $('.info_page').on('click', function(){
        $('.info_page').css('display','none');
    });
});
