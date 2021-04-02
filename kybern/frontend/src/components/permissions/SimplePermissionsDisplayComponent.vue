<template>

    <span>

        <b-button class="mr-1 mb-4 btn-sm outline-secondary" :id="'add_permission_button_' + modal" variant="outline-secondary"
            v-b-modal="'add_permission_modal_'  + modal">Add Permission</b-button>

        <add-permission-modal-component :default_selection=default_selection :role_to_edit=role_to_edit
            :item_name=item_name :item_id=item_id :item_model=item_model
            :modal_id="'add_permission_modal_'  + modal">
        </add-permission-modal-component>

        <b-button class="mr-1 mb-4 btn-sm" :id="'edit_permissions_button_' + modal" variant="outline-secondary"
            v-b-modal="'edit_permissions_modal_'  + modal">Edit Permissions</b-button>

        <edit-permissions-modal-component :permissions=permissions :item_name=item_name
            :item_id=item_id :item_model=item_model :modal_id="'edit_permissions_modal_'  + modal">
        </edit-permissions-modal-component>

        <b-button class="mr-1 mb-4 btn-sm"  v-if="user_permissions.apply_template" id="apply_templates"
            variant="outline-secondary" v-b-modal="'apply_template_modal_' + item_model">Apply Templates</b-button>
        <template-modal :scope=item_model :target_id=item_id :target_model=item_model></template-modal>

        <router-link id="group_permissions_button" :to="{ name: 'group-permissions', params: { group_pk: group_pk}}">
            <b-button class="mb-4 btn-sm" variant="outline-secondary">See All Permissions In Group</b-button>
        </router-link>

        <permissions-table-component :permissions=permissions class="my-2"></permissions-table-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import AddPermissionModalComponent from '../permissions/AddPermissionModalComponent'
import EditPermissionsModalComponent from '../permissions/EditPermissionsModalComponent'
import PermissionsTableComponent from '../permissions/PermissionsTableComponent'
import TemplateModal from '../templates/TemplateModal'


export default {

    components: { AddPermissionModalComponent, EditPermissionsModalComponent, PermissionsTableComponent, TemplateModal },
    props: ['permissions', 'item_id', 'item_model', 'item_name', 'modal_id', 'default_selection', 'role_to_edit'],
    created: function () {
        var alt_target = this.item_model + "_" + this.item_id
        this.checkPermissions({permissions: {"apply_template": {alt_target:alt_target} } })
            .catch(error => { console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            group_pk: state => state.group_pk,
            user_permissions: state => state.permissions.current_user_permissions
        }),
        modal: function() { if (this.modal_id) { return this.modal_id } else {return "default" } },
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions'])
    }

}

</script>