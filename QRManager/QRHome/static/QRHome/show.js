function printable(id){
 $('.qr').html("");
 $('.container').html("");
 if (id == -1) return


    $.ajax({
        type: "GET",
        url: "retrieve_2fa_code_image",
        data: {
          "id": id
        },
        success: function (data) {
          if (data["error"]=="error"){
            alert("Error")
            window.location.replace("")
          }
          var key_phrase = Object.entries(data).pop()[1]
          var counter = 0;

           $('#qr').append(`<h2 class="d-print-none">Your order is: ${key_phrase}</h2>`);
           $('#qr').append(`<h2 class="d-print-none">It is highly recommend you do no include this order when printing your codes</h2>`);

          for (const [key, value] of Object.entries(data)){
              if(key=="key-phrase"){
                continue;
              }
              var image = new Image();
              image.src = `data:image/png;base64,${value[0]}`
              qrs.push(image);

              if (key/4==0){
                $('#qr').append(`<div class="row row-${counter}">`);

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
        error: function (data) {
          alert("Error")
          window.location.replace("")
        },
      });
}