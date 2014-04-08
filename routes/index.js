
/*
 * GET home page.
 */

exports.index = function(req, res){
  res.render('index', { title: 'CloudStack Auto Deploy' });
};

exports.autodeploy = function(req, res){
  res.render('autodeploy', { title: 'CloudStack Auto Deploy' });
};