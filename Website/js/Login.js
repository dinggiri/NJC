var signinbtn = document.getElementById("signinbtn")
signinbtn.addEventListener('click', popup)
function popup() {
    var userid = document.getElementById("userid").value;
    var userpw = document.getElementById("userpw").value;
    
    if (userid == "dbstjs1008" && userpw == "1234") {
        alert("로그인 실패")
    }
}