db.contact_d_t_o.update({}, { $set: { 'v': true, 'lu': new Date() } }, { upsert: false, multi: true });
db.organization_d_t_o.update({}, { $set: { 'v': true, 'lu': new Date() } }, { upsert: false, multi: true });
db.publication_d_t_o.update({}, { $set: { 'v': true, 'lu': new Date() } }, { upsert: false, multi: true });
db.u_r_l_metadata_d_t_o.update({}, { $set: { 'lu': new Date() } }, { upsert: false, multi: true });
db.user_dto.update({}, { $set: { 'lu': new Date() } }, { upsert: false, multi: true });