define(['underscore', 'jquery', 'jquery-ui'], function(_, $) {
    var lastSearchedText;
    var searchResultsVisible = false;


    function showSearchResults(searchText, searchItems, map) {
        if (lastSearchedText === searchText)
            return;
        lastSearchedText = searchText;

        map.removeAllMarkers();
        var searchResultsDiv = $('#search-results-div');

        if (searchText) {
            // Perform each search
            _.each(searchItems, function(searchItem) {
                startAjaxSearch();
                $.ajax({
                    type: 'GET',
                    url: searchItem.url,
                    data: {
                        'search_text': $('#search-box').val(),
                        'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                    },
                    dataType: 'html'
                }).done(function(data) {
                    data = JSON.parse(data);
                    $(searchItem.listSelector).html('');
                    // Show number of results
                    var resultCount = data.results.length;
                    var resultsString = (resultCount >= 10 ? '10+' : resultCount) + ' results';
                    $(searchItem.toggleSelector).parent().next('.count').text(resultsString);
                    // Hide or show panel based on availability of results
                    if(resultCount) {
                        // Show panel
                        $(searchItem.toggleSelector).closest('.panel').show();
                        // Display results
                        _.each(data.results, function(item) {
                            $('<a>' + searchItem.linkText(item) + '</a>')
                                .addClass(searchItem.linkClass)
                                .attr('href', 'javascript:void(0)')
                                .attr('title', searchItem.linkText(item))
                                .data(item)
                                .wrap('<li></li>')
                                .parent()
                                .appendTo(searchItem.listSelector);
                        });
                        if (data) {
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
                        $('.' + searchItem.linkClass)
                            .click(searchItem.onclick)
                            .each(function (index, value) {
                                map.plotMarker($(value).data());
                            });
                    } else {
                        // Hide panel
                        $(searchItem.toggleSelector).closest('.panel').hide();
                    }
                }).fail(function() {
                    console.log(searchItem.name, 'search failed');
                }).always(function () {
                    endAjaxSearch();
                });
            });

            if (!searchResultsVisible) {
                searchResultsDiv.toggle('slide', { direction: 'up' }, 500);

                searchResultsVisible = true;
            }
        } else {
            if (searchResultsVisible) {
                searchResultsDiv.toggle('slide', { direction: 'up' }, 500);

                searchResultsVisible = false;
            }
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

    return { showResults: showSearchResults };
});