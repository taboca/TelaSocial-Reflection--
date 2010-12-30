/*!
 * TelaSocial Widgets
 */

	function Clock(container) {
		this.container = container
		this.data = new Date();
	    var clock_time = this.data.toLocaleTimeString();
		clock_time = clock_time.replace(/:..( [AP]M)$/, '$1'); 
		$('#'+this.container).html(clock_time);
		//window.setTimeout(Clock, 1000);
	}
	
	function VideoPlayer(container) {
		
	}

	var clockContainer = "container-1";

	function refresh() {
		var clock_1 = new Clock(clockContainer);
		//var clock_2 = new Clock('container-2');
		window.setTimeout(refresh, 1000);
	}

	$(document).ready(function() {	
		refresh();
	});
	
	
	