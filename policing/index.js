var express = require('express');
var app = express();
var router = express.Router();
var path = __dirname + '/static/';
var mysql = require('mysql');
var connection = mysql.createConnection({
  host     : 'policing.cke0kirlh7a4.us-east-1.rds.amazonaws.com',
  user     : 'nikhil',
  password : 'cs336shenoy',
  database : 'BarBeerDrinker'
});

connection.connect();

// app.set('view engine','jade');

query = "SELECT * from sells";


router.use(function(req, res,next) {
	console.log("/" + req.method);
	next();
});

router.get("/",function(req,res){
	res.sendFile(path + "index.html");
	connection.query(query, function(err,rows,fields) {
		// if(err) throw err;
		// console.log('The solution is: ',rows)
		res.render("sells",{items : rows});
		// res.send(rows);
	});

});

router.get("/about",function(req,res) {
	res.sendFile(path + "about.html");
});

router.get("/contact",function(req,res) {
	res.sendFile(path + "contact.html");
});

app.use("/",router);

var server = app.listen(3000, function () {
  var host = server.address().address;
  var port = server.address().port;

  console.log('Example app listening at http://%s:%s', host, port);
});
