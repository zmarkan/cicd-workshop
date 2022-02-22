var express = require('express');
var app = express();
var exports = module.exports = {};
var versionNumber = "0.0.1"
var content = ""
let PORT = process.env.PORT || 3232

function welcomeMessage(){
    var message = "Welcome to the CityJS CircleCI Demo!";
    return message;
}

content = welcomeMessage() + "\n Version Number: " + versionNumber

// set the view engine to ejs
app.set('view engine', 'ejs');

app.get('/', function (req, res) {
    // var message = "Hello World";
    res.render("index", {message: content});
});

var server = app.listen(PORT, function () {
    console.log("Node server is running on port: "+ server.address().port);
});

module.exports = server;
module.exports.welcomeMessage = welcomeMessage;