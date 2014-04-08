var fs = require('fs');

var db_master = "cldstkdbsrv01";
var db_slave = "cldstkdbsrv02";
var kvm_hosts = "cldstkkvm01,cldstkkvm02";
var web_hosts = "cldstkwebsrv01,cldstkwebsrv02";
var mysql_servers = "cldstkdbsrv01";

var cldstk_kvm = "";

for (var i in kvm_hosts.split(",")) {
	//console.log(kvm_hosts.split(",")[i]);
	cldstk_kvm = cldstk_kvm + kvm_hosts.split(",")[i] + "\n";
};
console.log(cldstk_kvm);

var cldstk_web = "";

for (var i in web_hosts.split(",")) {
	//console.log(web_hosts.split(",")[i]);
	cldstk_web = cldstk_web + web_hosts.split(",")[i] + "\n";
};
console.log(cldstk_web);

var hostfile = "[db_master]\n" + db_master + "\n\n[db_slave]\n" + db_slave +
				 "\n\n[cldstk_web]\n" + cldstk_web + "\n[cldstk_kvm]\n" +
				cldstk_kvm + "\n[mysql_servers]\n" + db_slave + "\n" + db_master + "\n";


fs.writeFile("hosttest", hostfile, function(err) {
    if(err) {
        console.log(err);
    } else {
        console.log("The file was saved!");
    }
}); 

var varsfile = "db_master: " + db_master + "\n" +
			   "db_slave: " + db_slave + "\n" +
				"cloud_repl_password: password" + "\n" +
				"mysql_root_password: PaSSw0rd1234" + "\n";


fs.writeFile("varstest", varsfile, function(err) {
    if(err) {
        console.log(err);
    } else {
        console.log("The file was saved!");
    }
}); 