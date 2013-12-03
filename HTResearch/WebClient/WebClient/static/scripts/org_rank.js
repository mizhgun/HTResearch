var lastIndex = 0;
var INCREMENT = 50;
var selectedSort = 'name';

function getRows(start, end, sortField) {
    $.ajax({
        type: 'GET',
        url: '/get_org_rank_rows/',
        data: {
            'start': start,
            'end': end,
            'sort': sortField,
            'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
        },
        success: function(data) {
            $(data).filter('.org-rank-row').each(function(index) {
                lastIndex++;
                $(this).children('.org-rank-index').text(lastIndex.toString());
                $('#org-rank-table-body').append($(this));
            });
        },
        dataType: 'html'
    });
}

function lazyLoadRows() {
    var start = lastIndex;
    var end = lastIndex + INCREMENT - 1;
    var sortField = selectedSort;
    getRows(start, end, sortField);
}

$(window).scroll(function () {
    if($(window).scrollTop() == $(document).height() - $(window).height()) {
        lazyLoadRows();
    }
})

$(function() {
    lazyLoadRows();
});