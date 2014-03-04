define(['underscore', 'jquery', 'jquery-ui'], function(_, $) {
    var lastSearchedText;

    var searchBox = $('#search-box');
    var searchResultsDiv = $('#search-results-div');

    // Move within search results by using up/down keys
    // Click link using enter
    searchBox.keydown(function(e) {
        if(e.keyCode === 38) { // up
            moveSelection(-1);
        } else if(e.keyCode === 40) { // down
            moveSelection(+1);
        } else if(e.keyCode === 13) { // enter
            clickSelection();
        }
    });

    // Highlight selected result
    searchBox.on('changeSelection', function(e, sel) {
        var results = searchResultsDiv.find('li');
        results.removeClass('active');
        results.eq(sel).addClass('active');
    });

    // Move the result selection index by an amount (usually +/- 1)
    function moveSelection(amount) {
        var resultCount = searchBox.data('resultCount') || 1;
        var sel = searchBox.data('selection') || 0;
        sel = (((sel + amount) % resultCount) + resultCount) % resultCount;
        searchBox.data('selection', sel).trigger('changeSelection', sel);
    }

    // Click the current selection
    function clickSelection() {
        var sel = searchBox.data('selection') || 0;
        searchResultsDiv.find('li').eq(sel).find('a').click();
    }

    function search(searchText, searchItems, map, reload) {
        if (!reload && lastSearchedText === searchText)
            return;
        lastSearchedText = searchText;

        map.removeAllMarkers();

        if (searchText) {
            // Keep track of number of results
            var resultCount = 0;
            searchBox.data('selection', 0);
            // Perform each search
            _.each(searchItems, function(searchItem) {
                // See if we want to search for this item
                var shouldSearch = $(':checkbox:checked[data-search=' + searchItem.name + ']').length > 0;
                if(shouldSearch) {
                    var searchQuery = searchBox.val();
                    // Search begin
                    startAjaxSearch();
                    // See if we should do a custom search or just an ajax call
                    var searchFn = searchItem.search || ajaxSearch;
                    // Retrieve search results
                    searchFn(searchQuery, function(results) {
                        resultCount += results.length;
                        searchBox.data('resultCount', resultCount);
                        // Show search results for this item
                        displaySearchResults(searchItem, results, map);
                        // Search end
                        endAjaxSearch();
                    }, searchItem);
                } else {
                    // Hide panel
                    $(searchItem.toggleSelector).closest('.panel').hide();
                }
            });
            searchResultsDiv.slideDown();
        } else {
            searchResultsDiv.slideUp();
        }
    }

    // Default ajax search function
    function ajaxSearch(searchQuery, ready, searchItem) {
        // Do an ajax call with the given url
        $.ajax({
            type: 'GET',
            url: searchItem.url,
            data: {
                'search_text': searchQuery,
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            dataType: 'html'
        }).done(function(data) {
            var results = JSON.parse(data).results;
            ready(results);
        }).fail(function(data) {
            console.log(searchItem.name, 'search failed');
            ready([]);
        });
    }

    // Display search results for a specific type of item
    function displaySearchResults(searchItem, results, map) {
        // Clear previous results
        $(searchItem.listSelector).html('');
        // Show number of results
        var resultCount = results.length;
        var resultsString = (resultCount > 10 ? '10+' : resultCount)
            + ' result'
            + (resultCount == 1 ? '' : 's');
        $(searchItem.toggleSelector).find('.count').text(resultsString);
        // Hide or show panel based on availability of results
        if(resultCount) {
            // Show panel
            $(searchItem.toggleSelector).closest('.panel').show();
            // Display results
            _.each(results, function(item) {
                $('<a>' + searchItem.linkText(item) + '</a>')
                    .addClass(searchItem.linkClass)
                    .attr('href', 'javascript:void(0)')
                    .click(function() {
                        if(searchItem.onclick) {
                            searchItem.onclick(item);
                        }
                    })
                    .data(item)
                    .wrap('<li></li>')
                    .parent()
                    .appendTo(searchItem.listSelector);

                map.plotMarker(item);
            });
            if (results.length) {
                $(searchItem.toggleSelector).closest('.panel').show();
                $(searchItem.toggleSelector).attr('data-toggle', 'collapse');
                $(searchItem.toggleSelector).removeClass('disabled');
                $(searchItem.collapseSelector).collapse('show');
            } else {
                $(searchItem.toggleSelector).closest('.panel').hide();
            }
            $(searchItem.toggleSelector).click(function (e) {
                e.preventDefault();
            });
            $('.modal').modal({ show: false });
        } else {
            // Hide panel
            $(searchItem.toggleSelector).closest('.panel').hide();
        }
    }

    var searchesPending = 0;
    function startAjaxSearch() {
        searchesPending++;
        if (searchesPending === 1) {
            $('#search-ajax-loader').removeClass('hidden');
        }
    }
    function endAjaxSearch() {
        searchesPending--;
        if (searchesPending === 0) {
            $('#search-ajax-loader').addClass('hidden');
        }
    }

    return { search: search };
});