function checkboxAction(){
    var checkbox = document.getElementById('myCheck')
    var text = document.getElementById('myInput')
    if(checkbox.checked == true){
        text.disabled = true
    } else {
        text.disabled = false
    }
}
