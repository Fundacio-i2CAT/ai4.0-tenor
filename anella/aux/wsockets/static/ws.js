$(document).ready(function() {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', function() {
	socket.emit('connected');
    });
    
    socket.on('running', function() {
	alert('HOLA');
	$('#init').html('<h1>INSTANCE RUNNING</h1>');
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
	var data = { 'name_image': $("#name_image").val(),
		     'name': $("#name").val(),
		     'picture': $("#picture").val(),
		     'cv': $("#cv").val()
		   };
	socket.emit("launch", {"data": data});
    });
    socket.on('my_response', function(message) {
	$('#init').html(message['data']);
    });
    
});
