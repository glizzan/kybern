<template>

    <span>

        <b-button class="mr-1 mb-4 btn-sm outline-secondary" :id="'add_permission_button_' + modal" variant="outline-secondary"
            v-b-modal="'add_permission_modal_'  + modal">Add Permission</b-button>

        <add-permission-modal-component :default_selection=default_selection :role_to_edit=role_to_edit
            :item_name=item_name :item_id=item_id :item_model=item_model
            :modal_id="'add_permission_modal_'  + modal">
        </add-permission-modal-component>

        <b-button class="mb-4 btn-sm" :id="'edit_permissions_button_' + modal" variant="outline-secondary"
            v-b-modal="'edit_permissions_modal_'  + modal">Edit Permissions</b-button>

        <edit-permissions-modal-component :permissions=permissions :item_name=item_name
            :item_id=item_id :item_model=item_model :modal_id="'edit_permissions_modal_'  + modal">
        </edit-permissions-modal-component>

        <permissions-table-component :permissions=permissions class="my-2"></permissions-table-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import AddPermissionModalComponent from '../permissions/AddPermissionModalComponent'
import EditPermissionsModalComponent from '../permissions/EditPermissionsModalComponent'
import PermissionsTableComponent from '../permissions/PermissionsTableComponent'


export default {

    components: { AddPermissionModalComponent, EditPermissionsModalComponent, PermissionsTableComponent },
    props: ['permissions', 'item_id', 'item_model', 'item_name', 'modal_id', 'default_selection', 'role_to_edit'],
    computed: {
        modal: function() { if (this.modal_id) { return this.modal_id } else {return "default" } }
    }

}

</script>