define([], function() {
    var OrgDataSource = function(options) {
        this._formatter = options.formatter;
        this._columns = options.columns;
    };

    OrgDataSource.prototype = {

        /**
         * Returns stored column metadata
         */
        columns: function() {
            return this._columns;
        },

        /**
         * Called when Datagrid needs data. Logic should check the options parameter
         * to determine what data to return, then return data by calling the callback.
         * @param {object} options Options selected in datagrid (ex: {pageIndex:0,pageSize:5,search:'searchterm'})
         * @param {function} callback to be called with the requested data.
         */
        data: function (options, callback) {

            var url = '/get-org-rank-rows/';
            var self = this;

            var request = {
                type: 'GET',
                url: '/get-org-rank-rows/',
                data: {
                    'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
                },
                dataType: 'text'
            };

            if (options.search) {
                // Search active. Add URL parameters for search
                request.data['search'] = options.search;
            }

            if (options.sortProperty) {
                if (options.sortDirection == 'asc')
                    request.data['sort'] = options.sortProperty;
                else
                    request.data['sort'] = '-' + options.sortProperty;
            }

            request.data['start'] = options.pageSize * options.pageIndex;
            request.data['end'] = request.data['start'] + options.pageSize - 1;

            // TODO: Column sort

            $.ajax(request).done(function (responseText) {
                var response = $.parseJSON(responseText);
                var data = new Array();
                for (var i = 0; i < response.data.length; i++)
                    data[i] = response.data[i]._data;
                var count = response.data.length;
                var startIndex = request.data['start'] + 1;
                var endIndex = startIndex + count - 1;
                var records = response.records; var page = options.pageIndex + 1;

                // Allow client code to format the data
                if (self._formatter) self._formatter(data, startIndex);

                // Return data to Datagrid
                callback({
                    data: data,
                    start: startIndex,
                    end: endIndex,
                    count: count,
                    pages: Math.ceil(records / options.pageSize),
                    page: page
                });
            });
        }
    }

    return OrgDataSource;
});