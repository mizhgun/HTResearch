//Search for all contacts linked in each organization
var orgs = db.organization_d_t_o.find({cs: {$not: {$size: 0}}});
while(orgs.hasNext()) {
    var org = orgs.next();
    var contact_ids = org.cs;
    for (var i = contact_ids.length - 1; i >= 0; i -= 1) {
        var id = contact_ids[i];
        var contact = db.contact_d_t_o.find({_id: id});
        if (!contact.hasNext()) {
            //Delete the references to contacts that no longer exist
            var removed = org.cs.splice(i, 1);
            print('Broken org->contact link found');
            print('Org: ');
            printjsononeline(org._id);
            print('Contact: ');
            printjsononeline(removed);
        }
    }
    db.organization_d_t_o.save(org);
}

//Search for all organizations linked in each contact
var contacts = db.contact_d_t_o.find({o: {$exists:true}});
while(contacts.hasNext()){
    var contact = contacts.next();
    var org = db.organization_d_t_o.find({_id: contact.o});
    if (!org.hasNext()) {
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

//Search for all organizations linked in each user
var users = db.user_d_t_o.find({o: {$exists:true}});
while(users.hasNext()){
    var user = users.next();
    var org = db.organization_d_t_o.find({_id: user.o});
    if (!org.hasNext()) {
        print('Broken user->org link found');
        print('User: ');
        printjsononeline(user._id);
        print('Org: ');
        printjsononeline(user.o);
        //Delete the references to organizations that no longer exist
        db.user_d_t_o.update({ '_id': user._id},
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
    for (var i = partners.length - 1; i >= 0; i -= 1) {
        var id = partners[i];
        var partner = db.organization_d_t_o.find({_id: id});
        if (!partner.hasNext()) {
            //Delete the references to organizations that no longer exist
            var removed = host_org.ps.splice(i, 1);
            print('Broken org->partner org link found');
            print('Org:');
            printjsononeline(host_org._id);
            print('Partner Org:');
            printjsononeline(removed);
        }
    }
    db.organization_d_t_o.save(host_org);
}