var overSnippets = "snippets/";

 $(document).ready(function() {
	
	$(".menu-link").click(function () { 
	});

   $("div.tab").hover(function() {
     $(this).addClass("tab-highlight");
   },function(){
     $(this).removeClass("tab-highlight");
   });

   $("div.tab").click(function() {
        $("div.tab").removeClass("tab-selected");
        $(this).addClass("tab-selected");
	document.location=$(this).find("a").attr("href");
   });

   buttons_over();

 });

function buttons_over() { 
                $(".button").hover(function() {
                        $(this).addClass("button-highlight");
                        },function(){
                        $(this).removeClass("button-highlight");
                });
		$(".button").click( function () { 
			document.location=$(this).find("a").attr("href");
		});

} 
