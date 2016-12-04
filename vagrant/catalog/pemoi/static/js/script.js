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

// Function to check if public category exists already
function catNameCheck() {
  // If "make public" is checked, check for duplicate name
  if ($("#new-public").prop("checked")) {
    $catName = $("#newcategory").val();
    // If we're on the edit category name page, pass category id to backend
    if ($("#cat-id").length) {
      $catId = $("#cat-id").val()
      $data = {catname: $catName, catid: $catId}
    }
    // If not editing category name, there is no ID to pass
    else {
      $data = {catname: $catName}
    }
    // Use Ajax to check category name in the background.
    $.ajax({
      type: 'POST',
      url: '/checkcatname',
      data: JSON.stringify($data),
      contentType: 'application/json; charset=utf-8',
      success: function(result) {
        if(result != "OK"){
          // If the public category already exists, disable submit and display
          // error.
          $("#catname-warning").html("A public category with this name already \
                                      exists. Please choose a different name.");
          $("#submit").prop("disabled", true);
          $("#submit").css("background-color", "#aaa")
        }
        else {
          // If all is good, make sure submit is enabled and everything looks
          // normal
          $("#catname-warning").html("");
          $("#submit").prop("disabled", false);
          $("#submit").css("background-color", "");
        }
      }
    });
  }
  else {
    // If "make public" is not checked, make sure that form looks normal and
    // submit is enabled.
    $("#catname-warning").html("");
    $("#submit").prop("disabled", false);
    $("#submit").css("background-color", "");
  }
}

// Trigger above function on either clicking the checkbox or leaving the text
// input field.
$("#new-public").on("change", catNameCheck);
$("#newcategory").on("blur", catNameCheck);
