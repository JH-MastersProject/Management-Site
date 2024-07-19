function generateQR() {
  $(".initial-options").remove();
  var tokenName = document.getElementById('name').value;
  var tokenHidden = document.getElementById('hide').checked;
  $.ajax({
    type: "GET",
    url: "generate_2fa_code",
    data: {
      "name": tokenName,
      "hide": !tokenHidden
    },
    success: function (data) {

      var image = new Image();
      image.src = `data:image/png;base64,${data}`


      $('.new-qr').append(`
        <div class="card">
          <img class="card-img-top-new" src="" alt="">
          <div class="card-body">
            <h5 class="card-title"></h5>
            <p class="card-text">This is your new 2-factor qr code. Download and print this QR code. Make sure to keep this code safe and do not lose it</p>
            <input type="button" onclick="printQR()" class="btn btn-primary" value="Print">
          </div>
        </div>`
      )

      $('.card-img-top-new').attr("src", image.src);

    },
    failure: function (data) {
    },
  });
}

var qrs = [];
function generateMultiQR() {
  var tokenName = document.getElementById('name').value.trim();
  var tokenHidden = document.getElementById('hide').checked;
  var tokenAmount = document.getElementById('amount').value;
  var keyPhrase = document.getElementById('keyphrase').value.trim();

  if (tokenAmount > 1){
      var phrases = keyPhrase.split(" ")
      if ( (phrases.length != tokenAmount) || ((new Set(phrases)).size !== phrases.length)){
            alert("Your phrase must be a series of strings, separated by a space, and equal to the length you selected above. Each string must be unique.")
            return
      }
  }

  if(tokenName == ""){
    alert("The name cannot be empty")
    return
  }

  if(tokenAmount < 1){
    alert("The number of codes cannot be less that 1.")
    return
  }

  if(tokenAmount==1){
    keyPhrase = "";
  }


  $(".initial-options").remove();

  $.ajax({
    type: "GET",
    url: "gen_multi_2fa_codes",
    data: {
      "name": tokenName,
      "hide": !tokenHidden,
      "amount": tokenAmount,
      "keyphrase": keyPhrase
    },
    success: function (data) {
      var counter = 0;
      for (const [key, value] of Object.entries(data)){
        var image = new Image();
        image.src = `data:image/png;base64,${value[0]}`
        qrs.push(image);

        if (key/4 == 0){
        $('.new-qr').append(`<div class="row row-${counter}">`);
        }

        $(`.row-${Math.floor(counter)}`).append(`<div class="col-3">
            <div class="card">
                <img class="card-img-top-new-${parseInt(key)+1}" src="" alt="">
                <h5 class="card-title text-center">${value[1]}</h5>
            </div></div>`
        )

        if (key+1/3 == 0){
        counter++;
        $('.new-qr').append(`<\div>`);
        }

        $(`.card-img-top-new-${parseInt(key)+1}`).attr("src", image.src);
      }





    },
    failure: function (data) {
    },
  });
}