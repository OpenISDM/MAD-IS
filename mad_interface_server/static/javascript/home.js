window.onload = function() {
    // Initialize all onclick events and div positioning
    init();

    $("#logoutView").on("click", logout);

    // If in data view mode, re-bind all onclick events
    // If in map view mode, disable POS and facility options and unbind events
    $("#switchMode").click(function() {
        if ($(this).find("i").hasClass("map")) {
            $(this).html("<i class=\"teal file icon\"></i>");
            $("#map-canvas").show();
            $("#tablecanvas").hide();
            google.maps.event.trigger(map, 'resize');
            map.setCenter(validCenter);
            location.reload();
        } else {
            $(this).html("<i class=\"teal map icon\"></i>");
            $("#map-canvas").hide();
            $("#tablecanvas").show();
        }
        $("#listPOS").toggle();
        $("#listFac").toggle();
        $("#facOptions").toggle();
        $("#posOptions").toggle();
        $("#posEdit").hide();
        $("#facEdit").hide();
    });

    $("#posOptions").click(function() {
        $("#posEdit").show();
        $("#facEdit").hide();
        $("#tablecanvas").hide();
    });


    $("#facOptions").click(function() {
        $("#facEdit").show();
        $("#posEdit").hide();
        $("#tablecanvas").hide();
    });
}

function init() {
    sidebarPosition();
    sidebarPopup();
    sidebarToggleEvent();
    $("#sidebar .item").on("click", sidebarToggleActiveElement);
    $("#facOptions").hide();
    $("#posOptions").hide();
    $("#tablecanvas").hide();
    $("#posEdit").hide();
    $("#facEdit").hide();
}

function sidebarPosition() {
    $("#menus .sidebar").each(function() {
        $(this).css("left", $("#sidebar").css("width"));
    });
    $("#mainCanvas").css("margin-left", $("#sidebar").css("width"));
}

function sidebarPopup() {
    $("#sidebar .item").popup({
        position: "right center",
        variation: "inverted"
    });
    $("#sidebar .item").on("hover", function() {
        if (!$(this).popup("is visible")) {
            $(this).popup("show");
        }
    });
}

// Set up sidebar toggle functionality
function sidebarToggleEvent() {
    $("#posMenu").sidebar({
        overlay: true
    }).sidebar("attach events", "#listPOS");
    $("#facMenu").sidebar({
        overlay: true
    }).sidebar("attach events", "#listFac");
}

// Set up sidebar active element functionality
function sidebarToggleActiveElement() {
    // Sidebar elements can be toggled to an active state
    if (!$(this).is("#switchMode")) {
        if ($(this).hasClass("active")) {
            $(this).removeClass("active");
        } else {
            $(this).addClass("active").siblings().removeClass("active");
        }
    }
    // Hide Sidebars on other actions
    if ($(this).is("#listPOS")) {
        $("#facMenu").sidebar("hide");
    }
    if ($(this).is("#listFac")) {
        $("#posMenu").sidebar("hide");
    }
   
    // Hide all sidebars and reset buttons to inactive state
    if ($(this).is("#switchMode")) {
        $("#menus .sidebar").each(function() {
            $(this).sidebar("hide");
        });
        $("#sidebar .item").each(function() {
            $(this).removeClass("active");
        });
    }
}

// Initialize a map with imported data (TODO!!)
function initialize() {
    // INITIALIZE MAP
    map = new google.maps.Map(document.getElementById('map-canvas'), {
        zoom: 11,
        maxZoom: 21,
        disableDefaultUI: true,
        disableDoubleClickZoom: true
    });

    setup();

    // CHECK MAP BOUNDS
    google.maps.event.addListener(map, 'center_changed', function() {
        var southPole = map.getBounds().getSouthWest().lat();
        var northPole = map.getBounds().getNorthEast().lat();
        if (southPole < -85 || northPole > 85) {
            map.setCenter(validCenter);
        }
        validCenter = map.getCenter();
    });

    // Hide sidebar when interacting with the map
    google.maps.event.addListener(map, "click", function() {
        $("#facMenu").sidebar("hide");
        $("#posMenu").sidebar("hide");
    });

    google.maps.event.addListener(map, "drag", function() {
        $("#facMenu").sidebar("hide");
        $("#posMenu").sidebar("hide");
    });
}

google.maps.event.addDomListener(window, 'load', initialize);

/// google map object
var rectangle;
var infoWindow = new google.maps.InfoWindow();
var facMarkers = [];
var posMarkers = [];
var geocoder = new google.maps.Geocoder();

var boundArray = [];    //record each POS bound range
var frontera = "";      //fusion table key
var posServer = [];
var fac = [];
var allWard = [];
var topicText = [];
var staticImg = [];

function setup() {
    var xmlhttp;
    if (window.XMLHttpRequest) { // code for IE7+, Firefox, Chrome, Opera, Safari
        xmlhttp = new XMLHttpRequest();
    } else { // code for IE6, IE5
        xmlhttp = new ActiveXObject("Microsoft.XMLHTTP");
    }
    xmlhttp.onreadystatechange = function() {
        if (xmlhttp.readyState == 4 && xmlhttp.status == 200) {
            //Receive Setup Information Server responses
            var configInfo = xmlhttp.responseText;
            //Add "()" and become json string for parsing
            var obj = eval("(" + configInfo + ")");

            city = obj.cityLocation;

            //Store the origin of coordinate that will be used to cut rectangle. 
            latLng = obj.coordinates;

            //Set the target that will be monitor, and finish geographic setting.
            setFacility(obj.data);
            setPOS(obj.posInfo);
            setCenter(latLng);
            setGeo(obj.wardInfo);
            showBoundary(obj.configInfo.key);
        }
    }
    xmlhttp.open("POST", "http://140.109.22.197/fetch/", true);
    xmlhttp.send("setupInfo");
}

function setFacility(facData) {
    if (facData.length == 0) {
        $('.ui.modal').modal('show');
    } else {
        for (var i = 0; i < facData.length; i++) {
            var facility = new Object();
            facility.myid = facData[i].id;
            facility.myname = facData[i].name;
            facility.mytype = facData[i].type;
            facility.kind = facData[i].category;
            facility.myward = facData[i].district;
            facility.address = facData[i].address;
            facility.tel = facData[i].telephone;
            facility.lat = facData[i].latitude;
            facility.lng = facData[i].longitude;
            facility.moreInfo = facData[i].description;
            fac.push(facility);
            createMarker(facility, 'fac',i);
        }
    }
}

function setPOS(posData) {
    for (var i = 0; i < posData.length; i++) {
        var pos = new Object();
        pos.myname = posData[i].id;

        pos.myward = posData[i].district;
        pos.cutWay = posData[i].method;
        pos.lat = posData[i].latitude;
        pos.lng = posData[i].longitude;
        pos.isexist = posData[i].isContact;
        posServer.push(pos);

        createMarker(pos, 'pos', i);
        setBound(pos, posData[i].bound_Latlng1, posData[i].bound_Latlng2);
        addToTable(pos, i);
        addPOSList(pos,i);
    }
}

function addPOSList(posServer, i){
	var html = $("#posMenu").html() + '<a class="ui fluid inverted purple button item" href="javascript:posPosition('+i+')">' + posServer.myname + '<\/a>';
	$("#posMenu").html(html);
}

function posPosition(index) {

    if (posServer[index].cutWay == 'District') {
        districtMethod(index);
    } else {
        rectangleMethod(index);
    }
	openInfoWindow(posMarkers[index], index, "");
}

function createMarker(place, placeType, index) {

	var content = "";
    var marker = new google.maps.Marker({
        position: new google.maps.LatLng(place.lat, place.lng),
        map: map,
        title: place.myname
    });

    if (placeType == 'fac') {
        marker.setIcon('/static/img/facility.png')
        marker.setMap(null);
        facMarkers.push(marker);

        content = getFacContent(index);
        
        google.maps.event.addListener(marker, 'click', function() {
    		openInfoWindow(marker, index, content);
  		});
    } else {
        if (place.isexist == true) {
            marker.setIcon('http://maps.google.com/mapfiles/ms/icons/green-dot.png');
        }
        posMarkers.push(marker);

        google.maps.event.addListener(marker, "click", function (e) { 
            switchMethod(index);
            openInfoWindow(marker, index, content);
            changeColumnVal(index,  getFacInfo(index));
	    });
    }
}

function getFacContent(index){

    var contentStr = '<div style="width: 400px; height: 150px">'+
              '<b>Name : ' + fac[index].myname + '<\/b><br>' + 
              '<b>District : ' + fac[index].myward + '<\/b><br>' + 
              '<b>Type : ' + fac[index].mytype + '<\/b><br>' +
              '<b>Category : ' + fac[index].kind + '<\/b><br>' +
              '<b>Address : ' + fac[index].address + '<\/b><br>' +
              '<b>Telephone : ' + fac[index].tel + '<\/b><br>' +
              '<b>Detail : ' + fac[index].moreInfo + '<\/b><br>' + '<\/div>';

    return contentStr;
} 

function switchMethod(index){
  if (posServer[index].cutWay == 'District') {
      posServer[index].cutWay = 'Rectangle';
      rectangleMethod(index);
  } else {
      posServer[index].cutWay = 'District';
      districtMethod(index);
  }
}

function openInfoWindow(marker, index, content) {

    if (content == "") {
        content = '<div style="width: 400px; height: 150px">' +
            '<b>Name : ' + posServer[index].myname + '<\/b><br>' +
            '<b>District : ' + posServer[index].myward + '<\/b><br>' +
            '<b>Number of facility : ' + getFacInfo(index) + '<\/b><br>' +
            '<b>Partition Method : ' + posServer[index].cutWay + '<\/b><br>';
    }

    if (infoWindow) {
        infoWindow.close();
    }
    infoWindow = new google.maps.InfoWindow({
        content: content
    });
    infoWindow.open(map, marker);
}

function setBound(pos, mixPoint, maxPoint) {

    //Saparate latitude and longitude by splitting the ',' character.
    var coordinates = latLng.split(",");

    //Calculate the distances from the latitude of origin to latitude of POS location and 
    //from the longitude of origin to longtitude of POS location.
    var dy = parseFloat(pos.lat) - parseFloat(coordinates[0]);
    var dx = parseFloat(pos.lng) - parseFloat(coordinates[1]);

    //Calculate which number of row and column will be assign.
    var qy = Math.floor(dy / 0.005) + parseFloat(1);
    var qx = Math.floor(dx / 0.01) + parseFloat(1);

    //Create new object that record the bounds of rectangle.
    var bound = new Object();

    if (pos.cutWay == "District") {
        bound.minLat = parseFloat(coordinates[0]) + ((parseFloat(0.005)) * qy) - parseFloat(0.005);
        bound.minLng = parseFloat(coordinates[1]) + ((parseFloat(0.01)) * qx) - parseFloat(0.01);
        bound.maxLat = parseFloat(coordinates[0]) + (parseFloat(0.005)) * qy;
        bound.maxLng = parseFloat(coordinates[1]) + (parseFloat(0.01)) * qx;
    } else {
        bound.minLat = mixPoint.split(",")[0];
        bound.minLng = mixPoint.split(",")[1];
        bound.maxLat = maxPoint.split(",")[0];
        bound.maxLng = maxPoint.split(",")[1];
    }
    bound.minPoint = bound.minLat + ',' + bound.minLng;
    bound.maxPoint = bound.maxLat + ',' + bound.maxLng;

    boundArray.push(bound);
}

function addToTable(pos, index) {

    var tr = $("<tr></tr>").addClass("dynamic_tr").attr("id", "trNo" + index);

    var tdName = $('<td nowrap="nowrap"><p>' + pos.myname + '<\/p></td>').attr("id", "tdName" + index);
    tr.append(tdName);

    var tdArea = $('<td nowrap="nowrap"><p>' + pos.myward + '<\/p></td>').attr("id", "tdArea" + index);
    tr.append(tdArea);

    var tdNumber = $('<td></td>').text(getFacInfo(index)).attr("id", "tdNum" + index);
    tr.append(tdNumber);

    var tdTxt = $("<td><a><i class=\"purple text file icon\"></i></a></td>").attr("index", index).attr("id", "tdTxt" + index);
    tdTxt.click(function() {
        var index = $(this).attr("index");
        fnOpen("Text", parseInt(index));
        index--;
    });
    tr.append(tdTxt);

    var tdImg = $("<td><a><i class=\"purple photo icon\"></i></a></td>").attr("index", index).attr("id", "btn" + index);
    tdImg.click(function() {
        var index = $(this).attr("index");
        fnOpen("Image", parseInt(index));
        index--;
    });
    tr.append(tdImg);

    $("#posTable").append(tr);
    postServer(index, "Download");
}

function getFacInfo(index) {
    var jsonArrayText = [];
    var num = 0;
    var html='';
    imgUrl = setImgInit(index);

    if (posServer[index].cutWay == 'District') {
        imgUrl += "&zoom=14"
        for (var k = 0; k < fac.length; k++) {
            if (fac[k].myward == posServer[index].myward) {
                num++;
                facElement = createFacElement(k);

                if ((imgUrl + setUrl(fac[k].lat, fac[k].lng)).length < 2000) {
                    imgUrl += setUrl(fac[k].lat, fac[k].lng);
                }
                jsonArrayText.push(facElement);
            }
        }
    } else {
        imgUrl += "&zoom=14"
        for (var m = 0; m < fac.length; m++) {
            if (((boundArray[index].minLat < fac[m].lat) && (fac[m].lat < boundArray[index].maxLat)) && ((boundArray[index].minLng < fac[m].lng) && (fac[m].lng < boundArray[index].maxLng))) {

                html += '<a class="ui fluid inverted purple button item" href="javascript:Fac_Position(' + m + ')">' + fac[m].myname + '<\/a>';
                num++;

                facElement = createFacElement(m);
                if ((imgUrl + setUrl(fac[m].lat, fac[m].lng)).length < 2000) {
                    imgUrl += setUrl(fac[m].lat, fac[m].lng);
                }
                jsonArrayText.push(facElement);
            }
        }
        $("#facMenu").html(html);
    }
    imgUrl += "&size=640x640&key=AIzaSyC0MXBPQYPcc3IAhEJJdCDE6bGPhFobPHo&sensor=false";

    jsonArrayText = JSON.stringify(jsonArrayText);
    topicText[index] = jsonArrayText;
    staticImg[index] = imgUrl;

    return num;
}

function setImgInit(index) {
    var imgCenterX = (parseFloat(boundArray[index].minLat) + parseFloat(boundArray[index].maxLat)) / 2;
    var imgCenterY = (parseFloat(boundArray[index].minLng) + parseFloat(boundArray[index].maxLng)) / 2;
    var url = "http://maps.googleapis.com/maps/api/staticmap?center=" + imgCenterX + "," + imgCenterY + "&markers=icon:http://www.worldvision.org.hk/images/icons/7_11_icon.png|" + posServer[index].lat + "," + posServer[index].lng;

    return url;
}

function createFacElement(index) {
    element = {
        "ID": fac[index].myid,
        "Name": fac[index].myname,
        "Type": fac[index].mytype,
        "Category": fac[index].kind,
        "District": fac[index].myward,
        "Address": fac[index].address,
        "Telephone": fac[index].tel,
        "Latitude": fac[index].lat,
        "Longitude": fac[index].lng,
        "MoreInfo": fac[index].moreinfo
    }
    return element;
}

function setUrl(latitude, longtitude) {
    url = "&markers=color:green|" + latitude + "," + longtitude;
    return url;
}

function setCenter(address) {
    geocoder.geocode({
        'address': address
    }, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            map.setCenter(results[0].geometry.location);
        }
    });
}

function setGeo(wardInfo) {
    for (var k = 0; k < wardInfo.length; k++) {
        allWard.push(wardInfo[k].District);
    }
}


function showBoundary(key) {
    borderlayer = new google.maps.FusionTablesLayer({
        query: {
            select: 'null',
            from: key
        },
        map: map,
        suppressInfoWindows: true
    });
    google.maps.event.addListener(borderlayer, 'click', function(e) {
        windowControl(e, infoWindow, map);
    });
}


function fnOpen(type, index) {
    var sFeatures = fnSetValues();
    switch (type) {
        case "Text":
            var sDialogArguments = topicText[index];
            var retValue = window.showModalDialog("/textView/", sDialogArguments, sFeatures);
            break;

        case "Image":
            var sDialogArguments = staticImg[index];
            var retValue = window.showModalDialog("/imgView/", sDialogArguments, sFeatures);
            break;

        default:
            break;
    }
}


function fnSetValues() {
    var iHeight = 300;
    var sFeatures = "dialogHeight: " + iHeight + "px;";
    return sFeatures;
}

// TODO
function postServer(index, purpose) {
    var serverUrl = "";
    var str = "";
    var hr = new XMLHttpRequest();

    switch (purpose) {
        case "Download":
            str = 'download$' + posServer[index].myname + '$' + topicText[index] + '$' + staticImg[index];
            serverUrl = "http://140.109.22.197/send/";
            break;

        case "Update":
            str = 'update$' + posServer[index].myname + '$' + posServer[index].cutWay + '$' + boundArray[index].minPoint + '$' + boundArray[index].maxPoint + '$' + topicText[index] + '$' + staticImg[index];
            serverUrl = "http://140.109.22.197/send/";
            break;

        default:
            break;
    }

    //hr.open("POST", serverUrl, true);
    //hr.send(str);
}

// SWITCH METHOD, DISTRICT METHOD, SWITCH AREA, SHOW FACILITY, RECTANGLE METHOD, SHOW REC, SHOW NEAR FAC, SHOW NEW RECT, POS_POSITION


function SwitchMethod(selector) {
    var posIndex = $(selector).attr("index");
    if (selector.options[selector.selectedIndex].text == 'District') {
        districtMethod(posIndex);
    } else {
        rectangleMethod(posIndex);
    }
    google.maps.event.trigger(posMarkers[posIndex], 'click');
    postServer(posIndex, "Update");
}

function switchArea(number) {
    for (var n = 0; n < allWard.length; n++) {
        if (posServer[number].myward == allWard[n]) {
            setCenter(city + posServer[number].myward);
            map.setZoom(12);
        }
    }
}

function showFacility(number) {
    var html = '';
    html += '<h1>' + posServer[number].myward + '</h1>';

    for (var n = 0; n < fac.length; n++) {
        if (fac[n].myward == posServer[number].myward) {
            facMarkers[n].setMap(map);
            html += '<a class="ui fluid inverted purple button item" href="javascript:Fac_Position(' + n + ')">' + fac[n].myname + '<\/a>';
        } else {
            facMarkers[n].setMap(null);
        }
    }

    $("#facMenu").html(html)
}

function Fac_Position(index) {
    openInfoWindow(facMarkers[index], index, getFacContent(index));
}

function districtMethod(index) {
  posServer[index].cutWay = 'District';
  switchArea(index);
  showFacility(index);
  checkRec();
}

function rectangleMethod(index) {
    posIndex = index;
    posServer[index].cutWay = 'Rectangle';
    showRec(index);
    map.setZoom(14);
    showNearFac(index);
    google.maps.event.addListener(rectangle, 'bounds_changed', showNewRect); //event active when rectangle is changed
}

function showRec(index) {

  checkRec();

  //Set bound range
  var bounds = new google.maps.LatLngBounds(
    new google.maps.LatLng(boundArray[index].minLat, boundArray[index].minLng),
    new google.maps.LatLng(boundArray[index].maxLat, boundArray[index].maxLng)
  );

  //Set rectangle properties
  rectangle = new google.maps.Rectangle({
    bounds: bounds,
    editable: true
  });

  rectangle.setMap(map);
}

function checkRec() {
  if (rectangle) {
    rectangle.setMap(null);
    google.maps.event.clearListeners(rectangle);
    rectangle = null;
  }
}


function showNearFac(index) {
    var minX = boundArray[index].minLng - (parseFloat(0.01)) * 3;
    var maxX = boundArray[index].maxLng + (parseFloat(0.01)) * 3;
    var minY = boundArray[index].minLat - (parseFloat(0.005)) * 3;
    var maxY = boundArray[index].maxLat + (parseFloat(0.005)) * 3;
    for (var k = 0; k < fac.length; k++) {
        if (((minY < fac[k].lat) && (fac[k].lat < maxY)) && (
            (minX < fac[k].lng) && (fac[k].lng < maxX))) {
            facMarkers[k].setMap(map);
        } else {
            facMarkers[k].setMap(null);
        }
    }
}

function showNewRect(event) {
    ne = rectangle.getBounds().getNorthEast();
    sw = rectangle.getBounds().getSouthWest();
    boundArray[posIndex].minLng = sw.lng();
    boundArray[posIndex].minLat = sw.lat();
    boundArray[posIndex].maxLng = ne.lng();
    boundArray[posIndex].maxLat = ne.lat();

    boundArray[posIndex].minPoint = boundArray[posIndex].minLat + ',' + boundArray[posIndex].minLng;
    boundArray[posIndex].maxPoint = boundArray[posIndex].maxLat + ',' + boundArray[posIndex].maxLng;

    openInfoWindow(posMarkers[posIndex],posIndex,"");
    changeColumnVal(posIndex,  getFacInfo(posIndex));

    postServer(posIndex, "Update");
}

function changeColumnVal(index, number) {
  index++;
  var cell = document.getElementById('posTable').rows[index].cells;
  cell[2].innerHTML = number;
}

function facHandle(){
    setTimeout('window.location.replace("http://140.109.22.197/admin/facilityview/")', 100);
}

function posHandle(){
    setTimeout('window.location.replace("http://140.109.22.197/admin/posview/")', 100);
}

function logout(){
    setTimeout('window.location.replace("http://140.109.22.197/admin/logout/")', 100);
}
