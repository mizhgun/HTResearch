$('.btn').click(function () {
    var expire = new Date();
    expire = new Date(expire.getTime() + 7776000000);
    document.cookie = "htresearchv2=amaterasu; path=/; expires=" + expire;

    window.location = '/get_started/';
});