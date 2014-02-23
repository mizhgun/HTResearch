define(['organization/org-datasource','jquery', 'fuelux/datagrid'], function(OrgDataSource, $) {
    $(function () {
        $('#view-all-orgs-nav').addClass('active');

        $('#org-rank-table').datagrid({
            dataSource: new OrgDataSource({
                // Column definitions for Datagrid
                columns: [
                    {
                        property: 'num',
                        label: '#',
                        sortable: false
                    },
                    {
                        property: 'name',
                        label: 'Name',
                        sortable: true
                    },
                    {
                        property: 'address',
                        label: 'Address',
                        sortable: false
                    },
                    {
                        property: 'phone_numbers',
                        label: 'Phone Numbers',
                        sortable: false
                    },
                    {
                        property: 'emails',
                        label: 'E-Mails',
                        sortable: false
                    },
                    {
                        property: 'organization_url',
                        label: 'Website',
                        sortable: false
                    },
                    {
                        property: 'facebook',
                        label: 'Facebook',
                        sortable: false
                    },
                    {
                        property: 'twitter',
                        label: 'Twitter',
                        sortable: false
                    }
                ],
                formatter: function (items, startIndex) {
                    $.each(items, function (index, item) {
                        item.num = (startIndex + index) + '<span style="display: none;" class="org-data-row-id">' + item.id + '</span>';
                        if (item.organization_url)
                            item.organization_url = '<a target="_blank" href="' + item.organization_url + '">Site</a>';
                        else
                            item.organization_url = '';
                        if (item.phone_numbers)
                            item.phone_numbers = item.phone_numbers.join(', ');
                        else
                            item.phone_numbers = '';
                        if (item.emails)
                            item.emails = item.emails.join(', ');
                        else
                            item.emails = '';
                        if (item.facebook)
                            item.facebook = '<a target="_blank" href="' + item.facebook + '">FB</a>';
                        else
                            item.facebook = '';
                        if (item.twitter)
                            item.twitter = '<a target="_blank" href="' + item.twitter + '">TW</a>';
                        else
                            item.twitter = '';
                    });
                }
            }),
            stretchHeight: true
        });

        $('#org-rank-table').on('dblclick', 'tbody > tr', function () {
            var id = $(this).find('.org-data-row-id').html();
            if (id)
                window.location.href = '/organization/' + id;
        });
    });
});
