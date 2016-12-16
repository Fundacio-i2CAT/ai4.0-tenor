$(document).ready(function() {

    var socket = io.connect(location.protocol + '//' + document.domain + ':' + location.port);
    socket.on('connect', function() {
	socket.emit('connected');
    });
    
    var launch = $('#launch');
    launch.on("click",function(event) {
	socket.emit("my_event", {data: $("#name_image").val()});
    });
    
    socket.on('my_response', function(message) {
	$('#init').html(message['data']);
    });
    
});
