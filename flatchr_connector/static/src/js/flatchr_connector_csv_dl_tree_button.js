odoo.define('elite_praxedo_sync_wizard.listview_button', function (require) {
    "use strict";

    var core = require('web.core');
    var ListView = require('web.ListView');
    var ListController = require("web.ListController");

    var IncludeListView = {

        renderButtons: function () {
            this._super.apply(this, arguments);
            if (this.modelName === "intervention.ticket") {
                var elite_praxedo_sync_wizard_tree_button = this.$buttons.find('button.o_elite_praxedo_sync_wizard_tree_button');
                elite_praxedo_sync_wizard_tree_button.on('click', this.proxy('call_elite_praxedo_sync_wizard'))
            }
        },
        call_elite_praxedo_sync_wizard: function () {
            var self = this;
            console.log('this: ' + this);
            var action = {
                type: "ir.actions.act_window",
                name: "Praxedo Synchronization",
                res_model: "elite.praxedo.sync.intervention.wizard",
                target: 'new',
                views: [[false, 'form']],
                view_type: 'form',
                view_mode: 'form',
                context: "{'default_res_model': 'intervention.ticket'}"
            }
            return this.do_action(action);
        },

    }
    ListController.include(IncludeListView);
});