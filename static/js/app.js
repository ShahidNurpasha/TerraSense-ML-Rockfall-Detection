document.addEventListener("submit", function(e){
  if(e.target.matches(".workflow")){
    const value=e.target.querySelector("select").value;
    if(value==="RESOLVED" && !confirm("Confirm that this alert can be marked resolved?")) e.preventDefault();
  }
});