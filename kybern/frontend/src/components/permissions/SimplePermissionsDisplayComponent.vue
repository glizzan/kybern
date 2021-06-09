<template>

    <span>

        <b-button class="mr-1 mb-4 btn-sm outline-secondary add-permission" :id="'add_permission_button'" variant="outline-secondary"
            v-b-modal="'add_permission_modal_' + add_target + '_' + default_selection">Add Permission</b-button>
        <permission-editor-component :mode="'add'" :edit_target=add_target :edit_change=default_selection>
        </permission-editor-component>

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
import PermissionEditorComponent from '../permissions/PermissionEditorComponent'
import PermissionsTableComponent from '../permissions/PermissionsTableComponent'
import TemplateModal from '../templates/TemplateModal'


export default {

    components: { PermissionEditorComponent, PermissionsTableComponent, TemplateModal },
    props: ['permissions', 'item_id', 'item_model', 'item_name', 'default_selection', 'role_to_edit'],
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
        add_target: function() {
            return this.item_model == "group" ? "community" : this.item_model + " '" + this.item_name + "'"
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions'])
    }

}

</script>