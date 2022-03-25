odoo.define('ela_hr', function (require) {
    "use strict";
    
    var CalendarModel = require('web.CalendarModel');
    
    CalendarModel.include({
        _getFullCalendarOptions: function () {
            var res = this._super.apply(this, arguments);
            return _.extend(res, {
                minTime: '08:00:00',
                maxTime: '22:00:00',
                slotDuration: '00:10:00',
            });
        },
    });
});