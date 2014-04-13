
/**
 * Module dependencies.
 */

var express = require('express');
var routes = require('./routes');
var posts = require('./routes/autodeploy.js');
var http = require('http');
var path = require('path');
var app = express();
app.locals.appname = 'CloudStack Auto Deploy';

// all environments
app.set('port', process.env.PORT || 3000);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'jade');
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.bodyParser());
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(express.cookieParser());
app.use(express.session({secret: '85A93087-78BC-4EB9-993A-A61FD144F6C9'}));


app.use(app.router);
app.use('/', express.static(__dirname + '/public'));
app.use('/acs/rpms/', express.static(__dirname + '/public/cloudstack.apt-get.eu/rhel/'));
app.use('/acs/rpms/', express.directory(__dirname + '/public/cloudstack.apt-get.eu/rhel/'));
app.use('/acs/templates/', express.static(__dirname + '/public/templates/'));
app.use('/acs/templates/', express.directory(__dirname + '/public/templates/'));

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

app.get('/', routes.index);
app.get('/autodeploy', routes.autodeploy);
app.post('/autodeploy/start', posts.start);

http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
