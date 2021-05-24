<template>

    <span>

        <form-button-and-modal v-if="edit_permission" :id_add=id_to_add :item_id=item_id :item_model=item_model>
        </form-button-and-modal>

        <b-icon-trash v-if="delete_permission" :id="'delete_' + item_model + '_button'" class="mr-2"
            @click="$emit('delete')" v-b-tooltip.hover :title="'delete ' + item_model"></b-icon-trash>

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


export default {

    components: { ItemPermissionsModal, FormButtonAndModal},
    props: ['item_id', 'item_model', 'item_name', 'edit_permission', 'delete_permission', 'id_add', 'export_url', 'export_text'],
    computed: {
        export_prompt: function() { if (this.export_text) { return this.export_text } else { return "export" } },
        id_to_add: function() { if (this.id_add) { return this.id_add } else { return "main" } }
    }

}

</script>

<style>
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