<template>

    <b-modal :id="modal_id" :title="title_string" size="xl" hide-footer>

        <simple-permissions-display-component :permissions=permissions :item_id=item_id
            :item_model=item_model :item_name=item_name></simple-permissions-display-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import SimplePermissionsDisplayComponent from '../permissions/SimplePermissionsDisplayComponent'


export default {

    props: ['item_id', 'item_model', 'item_name', 'id_add'],
    components: { SimplePermissionsDisplayComponent },
    store,
    created: function () {
        this.getPermissionsForItem({ item_id: this.item_id, item_model: this.item_model })
            .catch(error => {  this.error_message = error })
    },
    computed: {
        ...Vuex.mapGetters(['permissionsForItem']),
        title_string: function() { return "Permissions for " + this.item_model + " '" + this.item_name + "'" },
        permissions: function() {
            return this.permissionsForItem(this.item_id + "_" + this.item_model, true)
        },
        modal_id: function() {
            if (this.id_add) { return "item_permissions_modal_" + this.id_add }
            else { return "item_permissions_modal" }
        }
    },
    methods: {
        ...Vuex.mapActions(['getPermissionsForItem']),
    }


}

</script>

