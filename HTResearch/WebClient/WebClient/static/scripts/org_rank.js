var lastIndex = 0;
var INCREMENT = 50;
var selectedSort = 'name';

function trClick() {
    var id = $(this).attr('data-id');
    if (id) {
        window.location.href = '/organization/' + id;
    }
}
