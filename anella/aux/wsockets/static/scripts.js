// var socket = io.connect('http://localhost:9999', { 'forceNew': true });

// socket.on('news', function (data) {
//     socket.emit('my other event', { my: 'data' });
// });

var orchestrator_url = "http://localhost:8082/orchestrator/api/v0.1/service/instance";

function do_the_things(e) {
    $.ajax({
	url: orchestrator_url,
	type: "POST",
	data: JSON.stringify(instantiation_request),
	dataType: "json",
	contentType: "application/json; charset=utf-8",
	success: function(){
	    alert("SUCCESS");
	},
	error: function(){
	    alert("ERROR");
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
	"name_image" : "Miercoles",
	"vm_image_format" : "QCOW2",
	"tenor_url" : "http://localhost:4000",
	"vm_image" : "http://10.8.0.10/omupi40b.img",
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
