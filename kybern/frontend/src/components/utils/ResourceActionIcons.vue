<template>

    <span>

        <form-button-and-modal :id_add=id_to_add :item_id=item_id :item_model=item_model></form-button-and-modal>

        <take-action-component v-on:take-action="$emit('delete')" :verb="'delete ' + item_model"
            :alt_target="item_model + '_' + item_id" :response=response :unique=item_id>
            <b-icon-trash :id="'delete_' + item_model + '_button'" class="mr-2" v-b-tooltip.hover
                :title="'delete ' + item_model"></b-icon-trash>
        </take-action-component>

        <b-link variant="dark" :to="{ name: 'action-history',
                        params: {item_id: item_id, item_model: item_model, item_name: item_name }}">
            <b-icon-clock-history class="mr-2" :id="item_model + '_history_button'"
                v-b-tooltip.hover :title="item_model + ' history'"></b-icon-clock-history>
        </b-link>

        <b-icon-shield-lock :id="item_model + '_permissions'" class="mr-2" v-b-tooltip.hover
            :title="item_model + ' permissions'" v-b-modal="'item_permissions_modal_' + id_to_add"></b-icon-shield-lock>
        <item-permissions-modal :item_id=item_id :item_model=item_model :item_name=item_name :id_add=id_to_add>
            </item-permissions-modal>

        <b-button v-if="export_url" :href=export_url v-b-tooltip.hover :title="export_prompt" download
            class="mr-2 btn-small" variant="link"><b-icon-download></b-icon-download></b-button>

    </span>


</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import FormButtonAndModal from '../utils/FormButtonAndModal'
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    components: { ItemPermissionsModal, FormButtonAndModal, TakeActionComponent },
    props: ['item_id', 'item_model', 'item_name', 'id_add', 'export_url', 'export_text', 'response'],
    computed: {
        export_prompt: function() { if (this.export_text) { return this.export_text } else { return "export" } },
        id_to_add: function() { if (this.id_add) { return this.id_add } else { return "main" } }
    }

}

</script>

<style scoped>
    a {
        color: black
    }
    .btn-link {
        color: black;
        font-size: 80%;
        margin-left: 0;
        padding-left: 0;
        padding-right: 0;
    }
</style>