/** @odoo-module **/

import { registerMessagingComponent } from '@mail/utils/messaging_component';

const { Component } = owl;
const { useRef } = owl.hooks;
export class ActivityMarkDonePopover extends Component {
    //--------------------------------------------------------------------------
    // Handlers
    //--------------------------------------------------------------------------
    /**
     * @private
     */
    _onClickDone() { alert('a');}
}

registerMessagingComponent(ActivityMarkDonePopover);