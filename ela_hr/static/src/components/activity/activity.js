/** @odoo-module */
  
import { Activity } from '@mail/components/activity/activity';
import { patch } from 'web.utils';
import Dialog from 'web.Dialog';
import core from 'web.core';
const _t = core._t;

patch(Activity.prototype, 'ela_hr/static/src/components/activity/activity.js', {

    async _onClickNRP() {
        await this.activity.markAsDone({
            feedback: this._feedbackTextareaRef.el.value,
            /*: this.$('#nrp_check').prop('checked'),*/
        });
        this.trigger('reload', { keepChanges: true });
    }

});