/**
 * @param {String} [fileText] Record text from loading the file
 * @param {Object} [result] Record json object after parsing the json text.
 * @param {Array}  [originKey] Record facility's properties after parsing original json text .
 * @param {Array}  [reOrderData] Record multiple facilities's object when parsing json text and reorganize it.
 * @param {Array}  [fac] Store current kinds of facility such as school, hospital, etc.
 * @param {String} [selectedIndex] Store the selected index
 * @param {String} [typeVal] Store the value that user selected and is similar 'Type' .
 * @param {Array}  [service] Store what purpose faility can be used such as resuce, shelter ,etc.
 */

/*
  Description : 
    This function describe that store the text from loading user's computer xml file. 
    Then get properties from parsing it, and push them into each menu.
----------------------------------------------------------------------------------------------------------------*/

function loadFileAsText3() {
  var fileToLoad = document.getElementById("fileToLoad3").files[0];
  var fileReader = new FileReader();
  fileReader.onload = function(fileLoadedEvent) {
    var textFromFileLoaded = fileLoadedEvent.target.result;
    document.getElementById("inputTextToSave3").value = textFromFileLoaded;

    fileText = textFromFileLoaded;

    //Add "()" and become json string for parsing
    jsonText = eval("(" + fileText + ")");

    result = getResult();
    originKey = result.keyArray;
    reOrderData = result.facArray;


    for (var i = 0; i < originKey.length; i++) {
      addMenu(originKey[i]);
    }
  };
  fileReader.readAsText(fileToLoad, "UTF-8");
  document.getElementById('expand').className = 'ui green button';
}
/*--------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that parse multiple layer json text and get all keys and values. it can be recursive to be parsed again when the value still is jsonArray or jsonObject. then put scattered values to match the same properties and become a new facility object and array. 
----------------------------------------------------------------------------------------------------------------*/

function getResult() {
  var keyArray = [];
  var valueArray = [];
  var facArray = [];


  function parseData(input) {
    $.each(input, function(property, text) {
      if ($.type(text).toLowerCase() == 'string' ||
        $.type(text).toLowerCase() == 'number' ||
        $.type(text).toLowerCase() == 'null') {
        valueArray.push(text);
        if (keyArray.indexOf(property) == -1) {
          keyArray.push(property);
        }
      } else {
        parseData(text);
      }
    });
  }

  parseData(jsonText);


  //Calculate how many facilities that data have.
  var facNumber = valueArray.length / keyArray.length;

  //Declare a object that can be added key and value and insert it to array. 
  //Repeat these steps until there have no faility can be processed.
  for (var f = 0; f < facNumber; f++) {
    var facObj = {};
    for (var k = 0; k < keyArray.length; k++) {
      var number = (f * (keyArray.length)) + k;
      facObj[keyArray[k]] = valueArray[number];
    }
    facArray.push(facObj);
  }

  //return a json object
  return {
    keyArray: keyArray,
    facArray: facArray
  };
}
/*--------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that insert item into each selector and it can be regarded as option.
  Arguments :
    item - The one property of facility that will be added to the menu.
----------------------------------------------------------------------------------------------------------------*/

function addMenu(item) {
  for (var n = 1; n < 9; n++) {
    var selection = document.getElementById("select" + n);
    var option = document.createElement("option");
    option.text = item;
    selection.add(option);
  }
}
/*---------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that store the value which is similar the meaning of facility type and 
    search for what kind of facility that data include. Then show the table and choose the option.
----------------------------------------------------------------------------------------------------------------*/

function expand() {
  
  fac = [];
  //Find which is match with 'Type' and get its 'Type' naming.
  selectedIndex = document.getElementById("select2").selectedIndex;
  typeVal = document.getElementsByTagName("option")[selectedIndex].value;
  for (var i = 0; i < reOrderData.length; i++) {
    if (fac.indexOf(reOrderData[i][typeVal]) == -1 && reOrderData[i][typeVal] != "") {
      fac.push(reOrderData[i][typeVal]);
    }
  }
  categoryTable();
  document.getElementById('expand').className = 'ui disabled button';
  document.getElementById('next').className = 'ui green button';
  $("#expand").off();
  $("#next").on("click", next);
}
/*---------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that show the table which list all kind of facility text with menu and
    start to let user sort out. 
----------------------------------------------------------------------------------------------------------------*/

function categoryTable() {
  service = [];

  for (var f = 0; f < fac.length; f++) {
    //Declare a new row
    var tr = $("<tr></tr>").addClass("dynamic_tr").attr("id", "trNo" + f);

    var td_name = $('<td></td>').text(fac[f]).attr("id", "tdName" + f);
    tr.append(td_name);

    var td_kind = $("<td></td>");
    var td_select = $('<select></select>').attr("rowCount", f).attr("id", "choice" + f);

    //MAD category options
    var td_option = $('<option>Null</option>' +
      '<option>Shelter(Outdoor)</option>' +
      '<option>Shelter(Indoor)</option>' +
      '<option>Rescue</option>' +
      '<option>Medical</option>' +
      '<option>Livelihood</option>' +
      '<option>Volunteer</option>' +
      '<option>Transportation</option>' +
      '<option>Communication</option>'
    );

    //Store the value select when the selection have changed
    td_select.change(function() {
      var index = $(this).attr("rowCount");
      service[index] = this.options[this.selectedIndex].text;
    });

    td_select.append(td_option);
    td_kind.append(td_select);

    //The row be added to the table 
    tr.append(td_kind);
    $("#facTable").append(tr);
  }
}
/*---------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that show the table which list all facilities text with menu.
    And start to let user sort out. 
  Return Value : 
    dbData - The text including facility information will be sent to server.
----------------------------------------------------------------------------------------------------------------*/

function sendFacInfo() {
  var selectKey = getAllKey();

  //var facGroup = [];

  for (var i = 0; i < reOrderData.length; i++) {

      index = 1;
      facObj = {
        "purpose" : "facility",
        "id":"FAC" + randomNum(),
        "name":reOrderData[i][selectKey[index]],
        "type":reOrderData[i][selectKey[++index]],
        "category":classFac(reOrderData[i][typeVal]),
        "district":reOrderData[i][selectKey[++index]],
        "address":reOrderData[i][selectKey[++index]],
        "telephone":reOrderData[i][selectKey[++index]],
        "latitude":reOrderData[i][selectKey[++index]],
        "longitude":reOrderData[i][selectKey[++index]],
        "description":reOrderData[i][selectKey[++index]]
      };

      facObj = JSON.stringify(facObj);

      var hr = new XMLHttpRequest();
      var serverUrl = "/send/";
      hr.open("POST", serverUrl, true);
      hr.send(facObj);
  }
}
/*---------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that store selected mapping property of facility from each menu. 
  Return Value : 
    selectKey - Store each menu's option user choose.
----------------------------------------------------------------------------------------------------------------*/

function getAllKey() {
  var selectKey = [];
  for (var n = 1; n < 9; n++) {
    var x = document.getElementById("select" + n).selectedIndex;
    selectKey[n] = document.getElementsByTagName("option")[x].value;
  }
  return selectKey;
}
/*--------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that get what kind of facility depend on user's choice. 
  Arguments :
    kind - The purpose of facility such as shelter, rescue, etc.
----------------------------------------------------------------------------------------------------------------*/

function classFac(place) {
  var kind = "";
  for (var k = 0; k < fac.length; k++) {
    if (place == fac[k]) {
      kind = service[k];
    }
  }
  return kind;
}
/*--------------------------------------------------------------------------------------------------------------*/

/*
  Description : 
    This function describe that generate six digits randomly.
  Return Value : 
    A 6-digit number be ragard as partial of POS id.
----------------------------------------------------------------------------------------------------------------*/

function randomNum() {
  var digit = "";
  for (var i = 0; i < 6; i++) {
    digit += Math.floor(Math.random() * 10);
  }
  return digit;
}
/*--------------------------------------------------------------------------------------------------------------*/
