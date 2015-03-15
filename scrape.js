/* jshint node:true */
"use strict";

var Crawler = require("crawler");
var fs = require('fs');

var all_candidates = [];

var c = new Crawler({
    maxConnections : 10,
    // This will be called for each crawled page 
    callback : function (error, result, $) {
        // $ is Cheerio by default 
        //a lean implementation of core jQuery designed specifically for the server 
        
        var data = $(".candidate > .content").map(parseItem);

        Object.keys(data).forEach(function(key) {
        	if (!isNaN(key)) {
        		all_candidates.push(data[key]);
        	}
        });

		function parseItem(index, element) {

			return {
				 name: $(element).find('h3').text().trim(),
				 age: $(element).find('.age').text().trim(),
				 party: $(element).find('.party').text().trim(),
				 views: $(element).find('.views').text().trim(),
				 district: $(element).find('.district').text().trim()
				
			};
		}


    },
    onDrain: function() {
    	process.stdout.write(JSON.stringify(all_candidates));
    	process.exit(0);
    }
});
 
for (var i=0;i<=76;i++) {
	c.queue('http://vaalikone.yle.fi/eduskuntavaalit2015/vaaligalleria?empa=' + i);
}

