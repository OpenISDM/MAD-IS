// HTML SETUP
var page = 1;
var wardInfo = null;
var points = null;


$(document).ready(function() {
    document.getElementById("second").style.display = "none";
    document.getElementById("third").style.display = "none";
    document.getElementById("fourth").style.display = "none";
    $("#next").on("click", next);
    document.getElementById("prev").onclick = prev;
    document.getElementById("load1").onclick = showCityInfo;
    document.getElementById("load2").onclick = showPOSInfo;
    document.getElementById("confirm").onclick = completeSetup;
    document.getElementById("cancel").onclick = closeCheck;
});



function next() {
    switch (page) {
        case 1:
            next_step1();
            break;
        case 2:
            next_step2();
            break;
        case 3:
            next_step3();
            break;
        case 4:
            checkSetup();
            break;
        default:
            alert("Error on next()");
    }

}

function prev() {
    switch (page) {
        case 1:
            page += 1;
            break;
        case 2:
            prev_step1();
            break;
        case 3:
            prev_step2();
            break;
        case 4:
            prev_step3();
            break;
        default:
            alert("Error on prev()");
    }
}

// Go to step 2
function next_step1() {
    if (validateStep(coordinates)) {
        document.getElementById("first").style.display = "none";
        document.getElementById("second").style.display = "block";
        document.getElementById("active1").className = "ui disabled step";
        document.getElementById("active2").className = "ui active step";
        document.getElementById("header").innerHTML = "<h1>Insert District Information<br><span class=\"description\">Step 2 - Input district information.</span></h1>";
        document.getElementById("prev").className = "ui red button";
        document.getElementById("fileToLoad1").onchange = function() {
            loadFileAsText("fileToLoad1", "inputTextToSave1");
        };
        updateMap(map2, position);
        page += 1;
    } else {
        alert('Forms must be filled out');
    }
}

// Back to step 1
function prev_step1() {
    document.getElementById("first").style.display = "block";
    document.getElementById("second").style.display = "none";
    document.getElementById("active1").className = "ui active step";
    document.getElementById("active2").className = "ui disabled step";
    document.getElementById("header").innerHTML = "<h1>Find your Location<br><span class=\"description\">Step 1 - Search for location and press next</span></h1>";
    document.getElementById("prev").className = "ui disabled button";
    page -= 1;
}

// Go to step 3
function next_step2() {
    if (validateStep(wardInfo)) {
        document.getElementById("second").style.display = "none";
        document.getElementById("third").style.display = "block";
        document.getElementById("active2").className = "ui disabled step";
        document.getElementById("active3").className = "ui active step";
        document.getElementById("header").innerHTML = "<h1>Insert POS Information<br><span class=\"description\">Step 3 - Input POS information.</span></h1>";
        document.getElementById("fileToLoad2").onchange = function() {
            loadFileAsText("fileToLoad2", "inputTextToSave2");
        };
        updateMap(map3, position);
        page += 1;
    } else {
        alert('Forms must be filled out');
    }
}

// Back to step 2
function prev_step2() {
    document.getElementById("third").style.display = "none";
    document.getElementById("second").style.display = "block";
    document.getElementById("active2").className = "ui active step";
    document.getElementById("active3").className = "ui disabled step";
    document.getElementById("header").innerHTML = "<h1>Insert District Information<br><span class=\"description\">Step 2 - Input district information.</span></h1>";
    document.getElementById("next").innerHTML = "Next";
    page -= 1;
}


// Go to step 4
function next_step3() {
    //TODO: need to add validation
    if (validateStep(points)) {
        document.getElementById("third").style.display = "none";
        document.getElementById("fourth").style.display = "block";
        document.getElementById("active3").className = "ui disabled step";
        document.getElementById("active4").className = "ui active step";
        document.getElementById("header").innerHTML = "<h1>Insert Facility Data<br><span class=\"description\">Step 4 - Input facility information</span></h1>";
        document.getElementById("next").innerHTML = "Submit";
        document.getElementById("next").className = "ui disabled button";
        $("#next").off();
        document.getElementById("fileToLoad3").onchange = function() {
            loadFileAsText3("fileToLoad3", "inputTextToSave3");
            $("#expand").on("click", expand);
        };
        page += 1;
    } else {
        alert('Forms must be filled out');
    }
}


// Back to step 3
function prev_step3() {
    document.getElementById("fourth").style.display = "none";
    document.getElementById("third").style.display = "block";
    document.getElementById("active3").className = "ui active step";
    document.getElementById("active4").className = "ui disabled step";
    document.getElementById("header").innerHTML = "<h1>Insert POS Information<br><span class=\"description\">Step 3 - Input POS information.</span></h1>";
    document.getElementById("next").innerHTML = "Next";
    document.getElementById("next").className = "ui green button";
    $("#next").on("click", next);
    page -= 1;
}



function checkSetup() {
    $('.ui.modal')
        .modal('setting', 'closable', false)
        .modal('show');
}

function closeCheck() {
    $('.ui.modal')
        .modal('hide');
}

// check if you can combine this with Save() in inputFacData()
function completeSetup() {

    jsonData = createJsonText();
    jsonData = JSON.stringify(jsonData);

    var hr = new XMLHttpRequest();
    var serverUrl = "http://140.109.22.197/send/";
    hr.open("POST", serverUrl, true);
    hr.send(jsonData);

    sendFacInfo();
    document.getElementById('next').className = 'ui green button';
    document.getElementById('next').innerHTML = '<i class=\"loading icon\"></i> Saving';

    setTimeout('window.location.replace("http://140.109.22.197/admin/home/")', 90000);
}


// GLOBAL SETUP
function initialize() {
    //getPosInfo();
    loadMap();
    coordinates = "";
    var markers = [];

    google.maps.event.addListener(searchBox, 'places_changed', function() {
        var places = searchBox.getPlaces();

        if (places.length == 0) {
            return;
        }
        for (var i = 0, marker; marker = markers[i]; i++) {
            marker.setMap(null);
        }

        // For each place, get the icon, place name, and location.
        for (var i = 0, place; place = places[i]; i++) {
            var image = {
                url: place.icon,
                size: new google.maps.Size(71, 71),
                origin: new google.maps.Point(0, 0),
                anchor: new google.maps.Point(17, 34),
                scaledSize: new google.maps.Size(25, 25)
            };

            var marker = new google.maps.Marker({
                map: map1,
                icon: image,
                title: place.name,
                position: place.geometry.location
            });

            markers.push(marker);

            position = place.geometry.location;
            coordinates = (place.geometry.location.toString()).replace(/[\])}[{(]/g, "");
            cityLocation = document.getElementById('pac-input').value;
            map1.setCenter(place.geometry.location);
            map1.setZoom(12);
        }
    });
}

function loadMap() {
    //Load map1 and search box
    map1 = new google.maps.Map(document.getElementById('map-canvas1'), {
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        zoom: 2,
        minZoom: 2,
        maxZoom: 21,
        center: new google.maps.LatLng(0, 0)
    });

    var input = (document.getElementById('pac-input'));
    map1.controls[google.maps.ControlPosition.TOP_LEFT].push(input);
    searchBox = new google.maps.places.SearchBox((input));

    //Load map2
    map2 = new google.maps.Map(document.getElementById('map-canvas2'), {
        zoom: 12,
        maxZoom: 21,
        center: new google.maps.LatLng(0, 0),
        draggable: false,
        disableDefaultUI: true,
        disableDoubleClickZoom: true
    });

    //Load map3
    map3 = new google.maps.Map(document.getElementById('map-canvas3'), {
        zoom: 11,
        maxZoom: 21,
        center: new google.maps.LatLng(0, 0),
        draggable: false,
        disableDefaultUI: true,
        disableDoubleClickZoom: true
    });

    // MAP 1 bound check
    google.maps.event.addListener(map1, 'center_changed', function() {
        var southPole = map1.getBounds().getSouthWest().lat();
        var northPole = map1.getBounds().getNorthEast().lat();
        if (southPole < -85 || northPole > 85) {
            map1.setCenter(validCenter);
        }
        validCenter = map1.getCenter();
    });
}

function updateMap(mapID, position) {
    google.maps.event.trigger(mapID, 'resize');
    mapID.setCenter(position);
}

//FORM VALIDATION
function validateStep(check) {
    return (check != null && check != "");
}


//SETUP STEP 2 AND 3
function loadFileAsText(inputFileID, textareaID) {

    var fileToLoad = document.getElementById(inputFileID).files[0];

    var fileReader = new FileReader();
    fileReader.onload = function(fileLoadedEvent) {
        var textFromFileLoaded = fileLoadedEvent.target.result;
        document.getElementById(textareaID).value = textFromFileLoaded;
        xmlText = textFromFileLoaded;
    };
    fileReader.readAsText(fileToLoad, "UTF-8");
}


//SETUP STEP 2
function showCityInfo() {
    wardInfo = document.getElementById("inputTextToSave1").value;
    if (validateStep(wardInfo)) {
        $("#countryInfo").hide();
        showBoundary(document.getElementById('key').value);
        showWardBtn();
    } else {
        alert('Forms must be filled out');
    }
}


//SETUP STEP 2
function showBoundary(key) {
    borderlayer = new google.maps.FusionTablesLayer({
        query: {
            select: 'null',
            from: key
        },
        map: map2,
        suppressInfoWindows: true
    });
    map2.setZoom(11);
}

//SETUP STEP 2
function showWardBtn() {
    if (window.DOMParser) {
        parser = new DOMParser();
        xmlDoc = parser.parseFromString(xmlText, "text/xml");
    } else {
        // Internet Explorer
        xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
        xmlDoc.async = false;
        xmlDoc.loadXML(xmlText);
    }

    wardInfo = xmlText;

    for (var i = 0; i < xmlDoc.getElementsByTagName("District").length; i++) {
        //Fetch District value and Postal Code value
        region = xmlDoc.getElementsByTagName("Name")[i].childNodes[0].nodeValue;
        code = xmlDoc.getElementsByTagName("PostalCode")[i].childNodes[0].nodeValue;

        //Declare a New button and set properties
        var ward_btn = $('<div class="ui button"></div>').text(region + code).attr("id", region);

        //Google map jump to District Scene when click the button.
        ward_btn.click(function() {
            setCenter(cityLocation + $(this).attr("id"));
            map2.setZoom(13);
        });

        $("#myward").append(ward_btn);
    }
}

//SETUP STEP 2
function setCenter(address) {
    /*It is the process of finding associated geographic coordinates from other geographic data, 
    such as street addresses, or ZIP codes (postal codes).*/
    var geocoder = new google.maps.Geocoder();
    geocoder.geocode({
        'address': address
    }, function(results, status) {
        if (status == google.maps.GeocoderStatus.OK) {
            map2.panTo(results[0].geometry.location);
        }
    });
}

//SETUP STEP 3
function showPOSInfo() {
    pos = [];

    //check validation
    points = document.getElementById("inputTextToSave2").value;
    if (validateStep(points)) {
        $("#posInfo").hide();
    } else {
        alert('Forms must be filled out');
    }

    if (window.DOMParser) {
        parser = new DOMParser();
        xmlDoc = parser.parseFromString(xmlText, "text/xml");
    } else {
        // Internet Explorer
        xmlDoc = new ActiveXObject("Microsoft.XMLDOM");
        xmlDoc.async = false;
        xmlDoc.loadXML(xmlText);
    }

    for (var i = 0; i < xmlDoc.getElementsByTagName("POSSite").length; i = i + 50) {

        //Create new object to record each POS properties and push into an array.
        var posObj = {};
        posObj.ward = xmlDoc.getElementsByTagName("District")[i].childNodes[0].nodeValue;
        posObj.special_id = xmlDoc.getElementsByTagName("ID")[i].childNodes[0].nodeValue;
        posObj.lat = xmlDoc.getElementsByTagName("Latitude")[i].childNodes[0].nodeValue;
        posObj.lng = xmlDoc.getElementsByTagName("Longitude")[i].childNodes[0].nodeValue;
        pos.push(posObj);

        createMarker(posObj);
    }
}

//SETUP STEP 3
function createMarker(pos) {
    var posMarker = new google.maps.Marker({
        position: new google.maps.LatLng(pos.lat, pos.lng),
        map: map3,
        title: pos.special_id,
    });
}

function createJsonText() {

    key = document.getElementById('key').value;
    jsonText = {
        "purpose": "setup",
        "location": cityLocation,
        "latLng": coordinates,
        "posArray": pos,
        "wardInfo": wardInfo,
        "key": key
    };

    return jsonText;
}

google.maps.event.addDomListener(window, 'load', initialize);
