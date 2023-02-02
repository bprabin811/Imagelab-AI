
function handleFormSubmit(formId){
  let form = document.getElementById(formId);
  form.querySelector("input[type=submit]").addEventListener("click", function(e) {
        e.preventDefault(); // prevent the form from being submitted immediately
    let fileInput = document.getElementById(formId).querySelector("input[type=file]");
    console.log(fileInput)
    if (!fileInput.value) {
        document.getElementById("alert").style.display = "flex";
        document.getElementById("alert").style.backgroundColor ="#2c2c2e";
        document.getElementById("alert").style.padding = "4px 10px";
        document.getElementById("alert").style.borderRadius = "10px";
        document.getElementById("alert").style.position = "fixed";
        document.getElementById("alert").style.top = "50%";
        document.getElementById("alert").style.height = "150px";
        document.getElementById("alert").style.width = "350px";
        document.getElementById("alert").style.alignItems = "center";
        document.getElementById("alert").style.justifyContent = "center";
        return;
    }
    document.getElementById("loading-dialog").style.display = "block";

    setTimeout(function() {
      document.getElementById(formId).submit();
    }, 1000);
  });
  document.getElementById("closeAlert").addEventListener("click", function(e) {
    document.getElementById("alert").style.display = "none";
  });
}
handleFormSubmit('compress-form')
handleFormSubmit('conv-form')


