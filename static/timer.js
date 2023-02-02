var count = 120;
      var countdown = document.getElementById("countdown");

      function startCountdown() {
        var interval = setInterval(function() {
          count--;
          countdown.innerHTML = "Download link will expired within "+ count + " seconds";
          countdown.style.color = "green";
          countdown.style.fontSize = "16px";
          countdown.style.fontWeight = "bold";
          if (count === 0) {
            clearInterval(interval);
            countdown.innerHTML = "Link expired";
            countdown.style.color = "red";
            countdown.style.fontSize = "16px";
            countdown.style.fontWeight = "bold";
          }
        }, 1000);
      }
      startCountdown();