function checkWidth() {
  return window.innerWidth < 680;
}
function toggleNav() {
  if (checkWidth()) {
    var navList = document.getElementById("nav-list");
    var header = document.getElementById("header");
    var icon = document.getElementById("nav-toggle");

    if (navList.style.display === "flex") {
      navList.style.display = "none";
      icon.style.left = "0%";
      icon.style.top = "30%";
      icon.style.transform = "rotate(0deg)";
      icon.style.backgroundColor="#2c2c2e";
      header.classList.remove("expanded");
    } else {
      navList.style.display = "flex";
      icon.style.left = "0%";
      icon.style.top = "85%";
      icon.style.transform = "rotate(180deg)";
      icon.style.backgroundColor="#2c2c2e";
      header.classList.add("expanded");
    }
  }
}

  // Get the search input and button
  const searchInput = document.getElementById("search-input");
  const searchButton = document.getElementById("search-button");

  searchButton.addEventListener("click", function(event) {
    event.preventDefault(); // prevent form submission
    const searchTerm = searchInput.value.toLowerCase(); // get the search term
    const toolCols = document.getElementsByClassName("tool-col-2"); // get all the tool-col-2 elements

    // loop through each tool-col-2 element
    for (let i = 0; i < toolCols.length; i++) {
      const h1 = toolCols[i].getElementsByTagName("h1")[0]; // get the h1 element inside the tool-col-2 element
      const h1Text = h1.innerText.toLowerCase(); // get the text of the h1 element

      // check if the h1 text contains the search term
      if (h1Text.indexOf(searchTerm) !== -1) {
        toolCols[i].style.display = "block";
         // show the tool-col-2 element
} else {
  toolCols[i].style.display = "none";
}
}
});
