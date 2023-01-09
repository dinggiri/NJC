const modal = document.getElementById("white");
const openButton = document.getElementsByClassName("흰색유무");




function openModal() {
    modal.style.display = "flex";
}

document.getElementById("white").onclick = function(){
	this.style.backgroundColor ="blue";
};

document.getElementsByClassName("흰색유무").onclick = function(){
    document.getElementsById("white").style.display = "flex";
}

openButton.addEventListener('click', openModal);





//toggle menu
function toggleMenu() {
    document.getElementById("myToggle").classList.toggle("show");
}

window.onclick = function(event) {
    if (!event.target.matchesz('.whitebtn')) {
        var dropdowns = document.getElementsByClassName("white_content");
        var i;
        for (i=0; i<dropdowns.lenth; i++) {
            var openDropdown = dropdowns[i];
            if (openDropdown.classList.contains('show')) {
                openDropdown.classList.remove('show');
            }
        }
    }
}
