/*
    handle bulk student registration and deletion.
*/


// 1. BULK REGISTRATION

// Create textbox for adding multiple students.
// Since btnAddStu was created statically, we can directly
// call click event on it.
$("#btnAddStu").click(function() {
  $("#divUpdateClass").empty();
  $("#graphCanvas").empty();

  // First create a bootstrap card container
  var cardBulk = document.createElement('div');
  $(cardBulk).attr("class", "card");

  // Card Header
  var cardBulkHeader = document.createElement('div');
  $(cardBulkHeader).attr("class", "card-header");

  // Card body
  var cardBulkBody = document.createElement('div');
  $(cardBulkBody).attr("class", "card-body");

  // Card footer
  var cardBulkFooter = document.createElement('div');
  $(cardBulkFooter).attr("class", "card-footer");

  // Create the label for textarea and place it inside card header.
  var txtareaLabel = document.createElement("label");
  $(txtareaLabel).attr("for", "bulkStudentRegistrationTxt");
  $(txtareaLabel).html("FirstName, LastName, Email, Password");
  $(cardBulkHeader).append(txtareaLabel);

  // Create the textarea and place inside card body
  var txtarea = document.createElement("textarea");
  $(txtarea).attr("id", "bulkStudentRegistrationTxt");
  $(txtarea).attr("name", "bulkStudentRegistrationTxt");
  $(txtarea).attr("rows", 5);
  $(txtarea).attr("cols", 60);
  $(txtarea).attr("placeholder", "FirstName,LastName,email@email,Password");
  $(cardBulkBody).append(txtarea);
  //$("#divUpdateClass").append(txtarea);


  // Create submit button and place it inside the card footer
  var btn = document.createElement("button");
  $(btn).attr({"type": "button", "class": "btn btn-primary"});
  $(btn).attr("id", "btnBulkSubmit");
  $(btn).html("Bulk Submit");
  $(cardBulkFooter).append(btn);
  //$("#divUpdateClass").append(btn);

  // Organize the whole card and put it inside the parent div
  $(cardBulk).append(cardBulkHeader);
  $(cardBulk).append(cardBulkBody);
  $(cardBulk).append(cardBulkFooter);
  $("#divUpdateClass").append(cardBulk);

  // Add a div that will hold messages about how 
  // the bulk registration went.
  var bulk_msg_div = document.createElement("div");
  $(bulk_msg_div).attr({"id": "bulkMessageBox"});
  $("#divUpdateClass").append(bulk_msg_div);

});

// Since "#btnBulkSubmit" is a dynamically bound object,
// the event addition needs care:
//    https://stackoverflow.com/questions/203198/event-binding-on-dynamically-created-elements
$(document).on("click", "#btnBulkSubmit", function() {
  function show_bulk_registration_error(message){
    $("#bulkMessageBox").html(message);
    $("bulkStudentRegistrationTxt").html("");
    $("bulkStudentRegistrationTxt").css("borderColor", "red");
  }

  // Get the text placed in the textarea
  var bulk_info = $.trim($("#bulkStudentRegistrationTxt").val());

  // Check if the format is valid
  if (bulk_info == ""){
    show_bulk_registration_error("Please provide one student info per line:\n FirstName,LastName,email@email,Password");
    return;
  }
  else {
    // Extract individual lines and check for format
    var info_header = ["user_firstname", "user_lastname", "user_email", "user_password"];
    var lines = bulk_info.split('\n');
    var data_to_send = new Array(lines.length);

    for (var i = 0; i < lines.length; i++){
        var line_vals = lines[i].split(',');

        // There should be four values separated by comma.
        if (line_vals.length != 4){
            show_bulk_registration_error("Line " + (i + 1) + 
              ": Comma separated values needed: FirstName,LastName,email@email,Password");
            return;
        }

        // Check for each value: alphanumeric and at least 2 char in length
        for (var j = 0; j < line_vals.length; j++){
            if (line_vals[j].length < 2){
                show_bulk_registration_error("Line " + (i + 1) + " " + info_header[j] +
                  ": At least 2 characters needed.");
                return;
            }

            if (info_header[j] == "user_email" && line_vals[j].split("@").length != 2){
                show_bulk_registration_error("Line " + (i + 1) + " " + info_header[j] +
                  ": Incorrect email format.");
                return;
            }

            if (info_header[j] != "user_email" && !line_vals[j].match(/^[0-9a-zA-Z]+$/)) {
                show_bulk_registration_error("Line " + (i + 1) + " " + info_header[j] +
                  ": Only alphabet or numbers allowed.");
                return;
            }
        }

        // Attach the data for this student for sending.
        // Make it a dictionary directly mapping the key to the values.
        data_to_send[i] = {};
        for(var k = 0; k < info_header.length; k++){
            data_to_send[i][info_header[k]] = line_vals[k];
        }
    }

    // The data is fine, Send the student registration info.
    $.ajax({
        type: "POST",
        url: "/assessment/bulk/new",
        data: JSON.stringify(data_to_send),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response){
          // Clean up the textarea
          $("#bulkStudentRegistrationTxt").val("");

          // Display the registration status of each student in the message box
          var olist = document.createElement("ol");
          for(var k in response){
            var li = document.createElement("li");
            $(li).html(k + " => " + response[k]);
            olist.append(li);
          };

          $("#bulkMessageBox").html("");
          $("#bulkMessageBox").append(olist);

          console.log("Student registration successfully uploaded");
        },
        failure: function(err){
          console.log("Failed to upoload student registration. Try again.", err)
        }
    });
  }
});



// 2. BULK DELETION

function display_current_students(){
  // Given a logged in teacher, get relevant info
  // about all students under that teacher.
  $.ajax({
    type: "POST",
    url: "/assessment/current_students",
    contentType: "application/json; charset=utf-8",
    dataType: "json",
    success: function(all_stu_info){
      // Header
      var drop_header = document.createElement("h5");
      $(drop_header).html("Select students to drop.");

      // Create a form and show student info as checkbox input type
      var stu_drop_form = document.createElement("form");
      $(stu_drop_form).attr("id", "stuDropForm");

      // Display the each student info as a checkbox
      for(var stu_email in all_stu_info){
        // Each goes into a div: see bootstrap forms
        var stu_div = document.createElement("div");
        $(stu_div).attr("class", "form-check");

        var inp = document.createElement("input");
        $(inp).attr("class", "form-check-input");
        $(inp).attr("type", "checkbox");
        $(inp).attr("value", "");
        $(inp).attr("name", "checkboxDropStu");
        $(inp).attr("id", "dropStu_" + stu_email);
        $(inp).attr("data-user_email", stu_email);

        var lbl = document.createElement("label");       
        $(lbl).attr("for", "dropStu" + stu_email);
        $(lbl).attr("class", "form-check-label");
        $(lbl).html(stu_email + "," + all_stu_info[stu_email].join());

        // Pack the input and the label into the div
        $(stu_div).append(inp);
        $(stu_div).append(lbl);

        // Append the div to the main parent
        $(stu_drop_form).append(stu_div);

      };
      // Create submit button
      var btn = document.createElement("button");
      $(btn).attr({"type": "button", "class": "btn btn-primary"});
      $(btn).attr("id", "btnBulkDrop");
      $(btn).html("Bulk Drop");

      $("#divUpdateClass").append(drop_header);
      $("#divUpdateClass").append(stu_drop_form);
      $("#divUpdateClass").append(btn);
    },
    failure: function(err){
      console.log("Failed to retreive student info for the teacher. Try again.", err)
    }
  });
}

// Static button when clicked should display current students
// under the logged in teacher.
$("#btnDisplayStuToDrop").click(function() {

  $("#divUpdateClass").empty();
  $("#graphCanvas").empty();

  display_current_students();
});

$(document).on("click", "#btnBulkDrop", function() {
  // Extract all student emails that were selected for dropping.
  var checkboxes = document.getElementsByName("checkboxDropStu");
  var stu_emails_to_drop = [];
  for(var i = 0; i < checkboxes.length; i++){
    if (checkboxes[i].checked){
      stu_emails_to_drop.push($(checkboxes[i]).attr("data-user_email"));
    }
  }

  // POST to drop from class
  if (stu_emails_to_drop.length > 0){
    $.ajax({
        type: "POST",
        url: "/assessment/to_drop",
        data: JSON.stringify(stu_emails_to_drop),
        contentType: "application/json; charset=utf-8",
        dataType: "json",
        success: function(response){
        },
        failure: function(err){
          console.log("Failed to drop students from class. Try again.", err)
        }
    });

    $("#divUpdateClass").empty();
    display_current_students();
  }

});
