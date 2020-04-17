// Jquery function to implement collapsing/expanding lists of links

const slidingLists = () => {
	x=0; // running counter on # of phones being presented from slide-down
	$('#collapsingList li').slice(0, 0).show();
	$('#Collapsible').on('click', function (e) {
		// I add 5 to the counter, and call slidwDown animation on the visable links
		e.preventDefault();
		x += 5;
		$('#collapsingList li').slice(0, x).slideDown();
	});
	$('#Retractable').on('click', function (e) {
		// I subreact 5 to the counter, and call slideUp animation on the last 5 visible links
		e.preventDefault();
		x -= 5;
		$('#collapsingList li').slice(x, x+5).slideUp();
	});

}

// Cite this code to W3 schools as an edit of their collapsible button code
// https://www.w3schools.com/howto/howto_js_collapsible.asp
const proConTabs = () => {
	let coll = document.getElementsByClassName("Collapsible");
	let i;
	for (i = 0; i < coll.length; i++) {
			let collapseList = coll[i].nextElementSibling;
			collapseList.style.display = "none"
			coll[i].addEventListener("click", function() {	
				this.classList.toggle("active");
				let content = this.nextElementSibling;
				if (content.style.display != "none"){
				  content.style.display = "none";
				} else {
				  content.style.display = "initial";
				}
		  });
	}
}

$(document).ready(function () {
	slidingLists();	
	proConTabs();
});
