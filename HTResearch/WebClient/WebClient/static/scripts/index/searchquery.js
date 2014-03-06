define(['underscore', 'jquery', 'jquery-ui'], function(_, $) {
    var lastSearchedText;

    var searchBox = $('#search-box');
    var searchResultsContainer = $('#search-results-div');

    // Focus search box when typing
    $(document).keypress(function(e) {
        searchBox.focus();
    });

    // Hover to select search result
    $(document).on('mouseenter', '#search-results-div li', function() {
        searchResultsContainer.find('li').removeClass('active');
        $(this).addClass('active');
    });

    // Move within search results by using up/down keys
    // Click link using enter
    searchBox.keydown(function(e) {
        if(e.keyCode === $.ui.keyCode.UP) {
            moveSelection(-1);
            e.preventDefault();
        } else if(e.keyCode === $.ui.keyCode.DOWN) {
            moveSelection(+1);
            e.preventDefault();
        } else if(e.keyCode === $.ui.keyCode.ENTER) {
            clickSelection();
        }
    });

    // Move the result selection index by an amount (usually +/- 1)
    function moveSelection(amount) {
        var visibleResults = searchResultsContainer.find('.panel:visible li');
        var resultCount = visibleResults.length || 1;
        var index = visibleResults.index(visibleResults.filter('.active'));
        index = (((index + amount) % resultCount) + resultCount) % resultCount;

        var selection = visibleResults.eq(index);

        visibleResults.removeClass('active');
        selection.addClass('active');

        if(selection.length) {
            // Make sure panel containing selection is open
            selection.closest('.collapse').collapse('show');

            // Scroll to selection
            var top = selection.offset().top - searchResultsContainer.offset().top - searchResultsContainer.height() / 2
                + selection.height() / 2 + searchResultsContainer.scrollTop();
            searchResultsContainer.animate({ scrollTop: top }, { duration: 200, queue: false });
        }
    }

    // Click the current selection
    function clickSelection() {
        searchResultsContainer.find('li.active').find('a').click();
    }

    function search(searchText, searchItems, map, reload) {
        if (!reload && lastSearchedText === searchText)
            return;
        lastSearchedText = searchText;

        map.removeAllMarkers();

        // Change the icon back if a search is performed
        var icon = $('.collapse-icon');
        if (icon.hasClass('glyphicon-collapse-down')){
            icon.removeClass('glyphicon-collapse-down');
            icon.addClass('glyphicon-collapse-up');
        }

        if (searchText) {
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
            searchResultsContainer.slideDown();
        } else {
            searchResultsContainer.slideUp();
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
        var resultsString = resultCount
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