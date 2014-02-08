/*
    Paul Poulsen - 2014-02-05
 */
// Find all documents with a p1 field
db.contact_d_t_o.find({ 'p1': { $exists: true} }).forEach(function (x) {
    // Longs are stored in an object while regular numbers are ints
    if (Object.prototype.toString.apply(x.p1) == "[object NumberLong]")
        x.p = [x.p1.toNumber().toString()] // First convert to javascript number, then to string
        // without converting to a number first, we get "NumberLong\(1234567890123456\)"
    else
        x.p = [x.p1.toString()]; // convert directly to string
    db.contact_d_t_o.save(x); // save
});

// remove the old p1
db.contact_d_t_o.update({ 'p1': { $exists: true}},
    { $unset: {
        "p1": ""
    }},
    { multi: true});