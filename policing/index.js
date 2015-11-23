var express = require('express');
var app = express();
var router = express.Router();
var path = __dirname + '/static/';


router.use(function(req, res,next) {
	console.log("/" + req.method);
	next();
});

router.get("/",function(req,res){
	res.sendFile(path + "index.html");
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
