function submit_form()
{
  document.getElementById("oauth_form").submit();
}


function request_game()
{
  var uname = document.forms["game_request_form"].elements["user_name"].value;
  var level = document.forms["game_request_form"].elements["level_name"].value;
  window.location.href = window.location.href + uname + "/" + level;
}

function match_passwords()
{
  var first = document.getElementById('user_password');
  var second = document.getElementById('re_user_password');

  if (first.value != "" && first.value == second.value) {
      document.getElementById('re_user_password').style.borderColor = 'green';

      return true;

  } else {
    document.getElementById('re_user_password').style.borderColor = 'red';
  }
}

function match_class_name()
{
  var first = document.getElementById('user_class');
  var second = document.getElementById('re_user_class');

  if (first.value != "" && first.value == second.value) {
      document.getElementById('re_user_class').style.borderColor = 'green';
      return true;

  } else {
      document.getElementById('re_user_class').style.borderColor = 'red';
  }
}

function valid_class_name()
{
  var select_elem = document.getElementById('user_class');
  if (select_elem.value != ""){
    select_elem.parentElement.getElementsByTagName("label")[0].style.borderColor = 'green';
    return true;
  }
  else {
    select_elem.parentElement.getElementsByTagName("label")[0].style.borderColor = 'red';
  }
}

function submit_user_registration_form()
{
  if (valid_class_name() && match_passwords())
  {
    document.getElementById("user_register_form").submit();
  }
  else
  {
    console.log("Error encountered during user registration");
  }
}


function submit_teacher_registration_form()
{
  if (match_class_name() && match_passwords())
  {
    document.getElementById("user_register_form").submit();
  }
  else
  {
    console.log("Error encountered during user registration");
  }
}

