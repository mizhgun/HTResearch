define([], function() {
    function checkURL(field) {
        var url = field.value;
        if (!(/^https?:\/\//.test(url))) {
            url = 'http://' + url;
        }
        field.value = url
    }

    return { checkURL: checkURL };
});