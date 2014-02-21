$(document).ready(function (){
    $('#request-org-nav').addClass("active");
});

function checkURL(field) {
    var url = field.value;
    if (!(/^https?:\/\//.test(url))) {
        url = 'http://' + url;
    }
    field.value = url
}