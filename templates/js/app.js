$(function() {
	if ("WebSocket" in window) {
		ws = new WebSocket("ws://" + document.domain + ":" + location.port + "/dispatcher/ws");
		ws.onmessage = function(msg) {
			var message = JSON.parse(msg.data);
			$("p#log").append(message.msg + '<hr />');

			if (message.uuid === undefined)
				localStorage.removeItem('caliope_uuid_session')
			else if (message.uuid.length) {
				localStorage.caliope_uuid_session = message.uuid
			}
		};
	};

	$('#login_form input[name=login]').focus();

	$("#login_form").on('submit', function(e) {
		e.preventDefault();

		if ("caliope_uuid_session" in localStorage) {
			ws.send(JSON.stringify({
				'cmd' : 'authentication_with_uuid',
				'uuid' : localStorage.caliope_uuid_session
			}));
		} else {
			var login = $('#login_form input[name=login]');
			var password = $('#login_form input[name=password]');
			ws.send(JSON.stringify({
				'cmd' : 'authentication',
				'login' : $(login).val(),
				'password' : CryptoJS.SHA256( $(password).val() ).toString()
			}));

			$(login).val('');
			$(password).val('');
		}
	});

	window.onbeforeunload = function() {
		ws.onclose = function() {
		};
		ws.close()
	};

	sse = new EventSource('/event_from_server');
	sse.onmessage = function(message) {
		$('#output').html(message.data);
	}
});

