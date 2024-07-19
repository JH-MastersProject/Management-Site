function deactivate(button){
    if(button.value == -1) return;

    $.ajax({
        type: "GET",
        url: "deactivate_code",
        data: {
          "id": button.value
        },
        success: function (data) {        
            window.location.replace("/")
        },
        error: function (data) {
          alert("Error")
          window.location.replace("")
        },
      });
}

$( document ).ready(function() {
var deactivateModal = document.getElementById('deactivateModal')
var cButton = document.getElementById("confirmDelete")
cButton.value = -1
deactivateModal.addEventListener('show.bs.modal', function (event) {
    var button = event.relatedTarget
    var id = button.getAttribute('data-bs-id')
    cButton.value = id
})
deactivateModal.addEventListener('hide.bs.modal', function (event) {
    cButton.value = -1

})

});