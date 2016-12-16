$(document).ready(function() {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', function() {
	socket.emit('connected');
    });
    
    var launch = $('#launch');
    launch.on("click",function(event) {
	if ($('#name_image').val() === '') {
	    $('#init').html('<font color="red">You must provide an image name</font>');
	    return;
	}
	if ($('#name').val() === '') {
	    $('#init').html('<font color="red">You must provide a consumer name</font>');
	    return;
	}
	if ($('#picture').val() === '') {
	    $('#init').html('<font color="red">You must provide a picture URL</font>');
	    return;
	}
	if ($('#cv').val() === '') {
	    $('#init').html('<font color="red">You must provide a CV text</font>');
	    return;
	}
	$('#init').html('');
	socket.emit("launch", {data: $("#name_image").val()});
    });
    
    socket.on('my_response', function(message) {
	$('#init').html(message['data']);
    });
    
});
