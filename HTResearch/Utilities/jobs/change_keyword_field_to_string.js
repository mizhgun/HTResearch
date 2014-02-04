var c = db.organization_d_t_o.find();
while(c.hasNext()) {
	var org = c.next();
	var keywordDict = org.ks;
	var keywordList = [];
	for(key in keywordDict) {
		keywordList.push(key);
	}
	var keywordString = keywordList.join(' ');
	org.ks = keywordString;
	db.organization_d_t_o.save(org);
}