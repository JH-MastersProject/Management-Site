$( document ).ready(function() {

let scanner = new Instascan.Scanner({ video: document.getElementById('preview'), mirror:false });
  scanner.addListener('scan', function (content) {

    submit_2fa(content);
    // scanner.stop();


  });
  Instascan.Camera.getCameras().then(function (cameras) {
    if (cameras.length > 0) {
      scanner.start(cameras[0]);
    } else {
      console.error('No cameras found.');
    }
  }).catch(function (e) {
    console.error(e);
  });
});

function submit_2fa(content) {
    $.ajax({
      type: "GET",
      url: "debug_get",
      data: {
        "qr": content
      },
      success: function (data) {
          $("#ID").html("ID: " + data["id"])
          $("#TOKEN").html("TOKEN: " + data["token"])
          $("#ACTIVE").html("ACTIVE: " + data["active"])
          $("#HASH").html("HASH: " + data["hash"])

      },
      error: function (data) {
        $("#ID").html("ID: " + "INVALID CODE")
          $("#TOKEN").html("TOKEN: " + "INVALID CODE")
          $("#ACTIVE").html("ACTIVE: " + "INVALID CODE")
          $("#HASH").html("HASH: " + "INVALID CODE")
        //window.location.replace("/")
  
      },
    });
}