// github oauth signin
function githubOAuth() {
  console.log("Function githubOAuth called");
  $url = "https://github.com/login/oauth/authorize?client_id=d6957d4007ba48103730&scope=user:email&state=" + $state
  console.log($url);
  $.get($url, function(data, status){
    console.log(data, status);
  });
}



// Google oauth signin
function signInCallback(authResult){
  if(authResult['code']) {
    // Send one-time-use code to the server, if successful, display welcome message
    $.ajax({
      type: 'POST',
      url: '/gconnect?state='+$state,
      processData: false,
      contentType: 'application/octet-stream; charset=utf-8',
      data: authResult['code'],
      success: function(result) {
        if (result) {
          // console.log(result);
          if (result != "new") {
            $('#result').html('Login successful for:<br>' + result + '<br>Redirecting to start page ...')
            setTimeout(function() {
              window.location.href = '/index/';
            }, 3000);
          }
          else {
            $('#result').html('Thanks for signing in. Please complete the sign up. Redirecting ...')
            setTimeout(function() {
              window.location.href = '/completesignup/';
            }, 4000);
          }
        }
        else if (authResult['error']) {
          console.log("There was an error during authentication" + authResult['error']);
        }
        else {
          $('#result').html("Failed to make a server-side call. Check your configuration and console.");
        }
      }
    });
  }
}


// Facebook oauth signin
// FB SDK
window.fbAsyncInit = function() {
    FB.init({
      appId      : '1207930352610599',
      xfbml      : true,
      version    : 'v2.8'
    });
  };

(function(d, s, id){
   var js, fjs = d.getElementsByTagName(s)[0];
   if (d.getElementById(id)) {return;}
   js = d.createElement(s); js.id = id;
   js.src = "//connect.facebook.net/en_US/sdk.js";
   fjs.parentNode.insertBefore(js, fjs);
 }(document, 'script', 'facebook-jssdk'));

// FB login functions
function sendTokenToServer() {
  var auth_response = FB.getAuthResponse()
  var access_token = FB.getAuthResponse()['accessToken'];
  console.log('Welcome!  Fetching your information.... ');
  FB.api('/me', function(response) {
    console.log('Successful login for: ' + response.name);
    $.ajax({
      type: 'POST',
      url: '/fbconnect?state='+$state,
      processData: false,
      data: access_token,
      contentType: 'application/octet-stream; charset=utf-8',
      success: function(result) {
      // Handle or verify the server response if necessary.
      if (result) {
        if (result == "new") {
          $('#result').html('Thanks for signing in!<br>Please complete signup. Redirecting...')
          setTimeout(function() {
            window.location.href = "/completesignup";
          }, 4000);
        }
        else {
           $('#result').html('Welcome back, ' + result + '!<br>Redirecting to start page ...')
           setTimeout(function() {
             window.location.href = "/index"
           }, 2000);
         }
      } else {
        $('#result').html('Failed to make a server-side call. Check your configuration and console.');
         }
      }
    });
  });
}

// Close button
$(".close").on("click", function() {
  $(this).parent().remove();
});

// Check if public category exists upon input
$("#new-public").on("change", function(){
  if (this.checked) {
    $catname = $("#newcategory").val();
    console.log($catname);
    $.ajax({
      type: 'POST',
      url: '/checkcatname',
      data: $catname,
      success: function(result) {
        console.log(result)
        if(result != "OK"){
          $("#catname-warning").html("A public category with this name already exists. Please choose a different name.");
          $("#submit").prop("disabled", true);
          $("#submit").css("background-color", "#aaa")
        }
      }
    });
  }
  else {
    $("#catname-warning").html("");
    $("#submit").prop("disabled", false);
    $("#submit").css("background-color", "");
  }
});
