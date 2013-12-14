var lastIndex = 0;
var INCREMENT = 50;
var selectedSort = 'name';

function trClick() {
    var id = $(this).attr('data-id');
    if (id) {
        window.location.href = '/organization/' + id;
    }
}

function sortOnColumn() {
    var sort = $(this).attr('data-sort-field');
    var canSort = (typeof sort !== 'undefined' && sort !== false);
    if (canSort) {
        lastIndex = 0;
        selectedSort = sort;
        $('#org-rank-table-body').empty();
        lazyLoadRows();
    }
}

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
                $(this).dblclick(trClick);
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

$(window).scroll(function() {
    if($(window).scrollTop() == $(document).height() - $(window).height()) {
        lazyLoadRows();
    }
})

$(function() {
    lazyLoadRows();

    $('#org-rank-table thead th').click(sortOnColumn);
});