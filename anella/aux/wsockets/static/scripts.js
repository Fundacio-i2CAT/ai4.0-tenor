
// socket.on('news', function (data) {
//     socket.emit('my other event', { my: 'data' });
// });

var catalog_url = "http://localhost:5000/launch";

$("#name_image").focus();
alert(document.domain+":"+location.port);

var socket = io.connect('http://' + document.domain + ':' + location.port);
socket.on('connect', function () {
    alert(this.socket.sessionid);
});

// socket.on('echo', function(data){
//     $('#progress').html('<p>'+data.echo+'</p>');
// });
function send(){
    socket.emit('send_message', {message : $('#name').val()});
}

function do_the_things(e) {
    send();
    instantiation_request['context']['consumer_params'][0]['fields'] =
	[
            {
		"required" : true,
		"name" : "name",
		"desc" : "Name of the consumer",
		"value" : $("#name").val()
            },
            {
		"required" : true,
		"name" : "picture",
		"desc" : "Consumer server Picture",
		"value" : $("#picture").val()
            },
            {
		"required" : true,
			"name" : "cv",
		"desc" : "CV del consumer",
		"value" : $("#cv").val()
            }
	];
 
    $.ajax({
	url: catalog_url,
	type: "POST",
	data: JSON.stringify(instantiation_request),
	dataType: "json",
	contentType: "application/json; charset=utf-8",
	success: function(){
	    $("#progress").html("SUCCESS");
	},
	error: function(){
	    $("#progress").html("ERROR");
	}});
}

var launch = $('#launch');
launch.on("click", do_the_things);


var instantiation_request = {
    "context" : {
	"runtime_params" : [
            {
		"name" : "wwwwww",
		"desc" : "sssssss"
            }
	],
	"public_network_id" : "71257860-3085-40bb-b009-5f12c688cdfb",
	"pop_id": 21,
	"name_image" : "sOcKeTs",
	"vm_image_format" : "openstack_id",
	"tenor_url" : "http://localhost:4000",
	"vm_image" : "5d4fdb85-3e7a-4e92-be67-72214a61275d",
	"flavor" : "VM.M1",
	"consumer_params" : [
            {
		"path" : "/var/www/html/index.html",
		"fields" : [
                    {
			"required" : true,
			"name" : "name",
			"desc" : "Name of the consumer",
			"value" : "Example deployment"
                    },
                    {
			"required" : true,
			"name" : "picture",
			"desc" : "Consumer server Picture",
			"value" : "http://lorempixel.com/400/200/"
                    },
                    {
			"required" : true,
			"name" : "cv",
			"desc" : "CV del consumer",
			"value" : "laksjd laksdj laksjd laks jdlkas jdlkas jd"
                    }
		]
            },
            {
		"path" : "/root/chequeo.txt",
		"content" : "YO ESTUVE AQUI"
	    }
	]
    }
};
