//Search for all contacts linked in each organization
var orgs = db.organization_d_t_o.find({cs: {$not: {$size: 0}}});
while(orgs.hasNext()) {
    var org = orgs.next();
    var contact_ids = org.cs;
    contact_ids.forEach(function(c_id, key) {
        var contact = db.contact_d_t_o.find({_id: c_id});
        if (contact.toArray().length === 0) {
            //Delete the references to contacts that no longer exist
            var removed = orgs.cs.splice(key, 1);
            print('Broken org->contact link found');
            print('Org: ');
            printjsononeline(org._id);
            print('Contact: ');
            printjsononeline(removed);
        }
    });
    db.organization_d_t_o.save(org);
}

//Search for all organizations linked in each contact
var contacts = db.contact_d_t_o.find({o: {$exists:true}});
while(contacts.hasNext()){
    var contact = contacts.next();
    var org = db.organization_d_t_o.find({_id: contact.o});
    if (org.toArray().length === 0) {
        print('Broken contact->org link found');
        print('Contact: ');
        printjsononeline(contact._id);
        print('Org: ');
        printjsononeline(contact.o);
        //Delete the references to organizations that no longer exist
        db.contact_d_t_o.update({ '_id': contact._id},
        { $unset: {
            "o": ""
        }});
    }
}

//Search all partner organizations linked in each organization
var host_orgs = db.organization_d_t_o.find({ps: {$exists: {$not: {$size: 0}}}});
while(host_orgs.hasNext()) {
    var host_org = host_orgs.next();
    var partners = host_org.ps;
    partners.forEach(function(partner, key){
        if (db.organization_d_t_o.find({_id: partner._id}).toArray().length === 0) {
            //Delete the references to organizations that no longer exist
            var removed = host_org.ps.splice(key, 1);
            print('Broken org->partner org link found');
            print('Org:');
            printjsononeline(org._id);
            print('Partner Org:');
            printjsononeline(removed);
        }
    });
    db.organization_d_t_o.save(host_org);
}