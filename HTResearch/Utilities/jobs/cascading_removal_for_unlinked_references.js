//Search for all contacts linked in each organization
var orgs = db.organization_d_t_o.find({cs: {$exists:true}, $where:'this.cs.length>0'});
while(orgs.hasNext()) {
    var org = orgs.next();
    var contact_ids = org.cs;
    contact_ids.forEach(function(c_id, key) {
        var contact = db.contact_d_t_o.find({_id: c_id});
        if (contact.toArray().length === 0) {
            //Delete the references to contacts that no longer exist
            contact_ids.splice(key, 1);
        }
    });
    //Unset the entire property if none left
    if (contact_ids.length === 0) {
        db.organization_d_t_o.update({ '_id': org._id},
        { $unset: {
            "cs": ""
        }});
    } else {
        org.cs = contact_ids;
        db.organization_d_t_o.save(org);
    }
}

//Search for all organizations linked in each contact
var contacts = db.contact_d_t_o.find({o: {$exists:true}});
while(contacts.hasNext()){
    var contact = contacts.next();
    var org = db.organization_d_t_o.find({_id: contact.o});
    if (org.toArray().length === 0) {
        //Delete the references to organizations that no longer exist
        db.contact_d_t_o.update({ '_id': contact._id},
        { $unset: {
            "o": ""
        }});
    }
}

//Search all partner organizations linked in each organization
var host_orgs = db.organization_d_t_o.find({ps: {$exists:true}, $where:'this.ps.length>0'});
while(host_orgs.hasNext()) {
    var host_org = host_orgs.next();
    var partners = host_org.ps;
    partners.forEach(function(partner, key){
        if (db.organization_d_t_o.find({_id: partner._id}).toArray().length === 0) {
            //Delete the references to organizations that no longer exist
            partners.splice(key, 1);
        }
    });
    //Unset the entire property if none left
    if (parnters.length === 0) {
        db.organization_d_t_o.update({ '_id': host_org._id},
        { $unset: {
            "ps": ""
        }});
    } else {
        host_org.ps = partners;
        db.organization_d_t_o.save(org);
    }
}