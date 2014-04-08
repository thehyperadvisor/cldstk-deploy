var fs = require('fs');

//var db_master = "cldstkdbsrv01";
//var db_slave = "cldstkdbsrv02";
//var kvm_hosts = "cldstkkvm01,cldstkkvm02";
//var web_hosts = "cldstkwebsrv01,cldstkwebsrv02";

exports.start = function(req, res){
    var db_master = req.body.db_master.toString().replace(',',''),
        db_slave = req.body.db_slave.toString().replace(',',''),
        kvm_hosts = req.body.kvm_hosts,
        web_hosts = req.body.web_hosts,
        nfs_server = req.body.nfs_server.toString().replace(',',''),
        nfs_path = req.body.nfs_path.toString().replace(',','')

    var cldstk_kvm = "";

    for (var i in kvm_hosts.split(",")) {
    	//console.log(kvm_hosts.split(",")[i]);
    	cldstk_kvm = cldstk_kvm + kvm_hosts.split(",")[i] + "\n";
    };
    //console.log(cldstk_kvm);

    var cldstk_web = "";

    for (var i in web_hosts.split(",")) {
    	cldstk_mgmt = web_hosts.split(",")[0];
    	cldstk_web = cldstk_web + web_hosts.split(",")[i] + "\n";
    };
    //console.log(cldstk_web);

    var hostfile = "[localhost]\n127.0.0.1\n\n" +
                    "[db_master]\n" + db_master + "\n\n[db_slave]\n" + db_slave +
    				"\n\n[cldstk_web]\n" + cldstk_web + "\n[cldstk_kvm]\n" +
    				cldstk_kvm + "\n[mysql_servers]\n" + db_slave + "\n" + db_master + "\n" +
                    "\n[cldstk_mgmt]\n" + cldstk_mgmt + "\n";


    fs.writeFile("./ansible/hosts", hostfile, function(err) {
        if(err) {
            console.log(err);
        } else {
            console.log("The host file was saved!");
        }
    }); 

    var varsfile = "---\n" + 
                   "master: " + db_master + "\n" +
    			   "slave: " + db_slave + "\n" +
    				"cloud_repl_password: password" + "\n" +
    				"mysql_root_password: PaSSw0rd1234" + "\n" +
                    "nfs_server: " + nfs_server + "\n" +
                    "nfs_path: " + nfs_path + "\n";


    fs.writeFile("./ansible/vars_file.yml", varsfile, function(err) {
        if(err) {
            console.log(err);
        } else {
            console.log("The vars file was saved!");
        }
    }); 
    res.send({success:"success"});
    res.end();
};

