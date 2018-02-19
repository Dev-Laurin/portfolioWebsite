
//HTTP Server
var http = require("http"),
	port = 3000;

var server = http.createServer(function(request,response){
	response.writeHeader(200, {"Content-Type": "text/plain"}); 
	response.write("!"); 
	response.end(); 
});

//server.listen(port); 
console.log("Server Running on port: " + port + ".\nLaunch http://localhost:" + port); 


//Mongoose-MongoDB
var mongoose = require("mongoose");  

//attributes for our documents
var Schema = mongoose.Schema; 

//create a schema
var userSchema = new Schema({
	name: String
}); 

//need a model using it
var user = mongoose.model('User', userSchema); 

//make it available to use in node applications
module.exports = user; 

//mongoose deprecated open() this is openUri from:
//https://stackoverflow.com/questions/45023793/mongoose-error-open-is-deprecated-in-mongoose-4-11-0#45571678
var options = {
	useMongoClient: true, 
	socketTimeoutMS: 0, 
	keepAlive: true, 
	reconnectTries: 30
}
mongoose.connect('mongodb://127.0.0.1/', options);


//Express
var express = require('express'); 
var app = express();  
app.use(express.static(__dirname + '/public')); 

app.get('/', function(req,res){
	res.sendFile('./public/html/index.html', {"root":__dirname});
});

 http.createServer(app).listen(port); 
