<template>

    <span>

        <h5 class="mb-3">{{ title_string }}</h5>

        <!-- Advanced Permissions & Templates-->

        <router-link :to="{ name: 'advanced-permissions', params: { item_id: final_item_id, item_model: final_item_model} }">
            <b-button class="mb-1 btn-sm">View Advanced Permissions</b-button>
        </router-link>

        <router-link v-if="user_permissions.apply_template"
                :to="{ name: 'item-templates', params: {scope: final_item_model, target_id: final_item_id, target_model: final_item_model} }">
            <b-button class="mb-1 btn-sm" id="apply_templates">Apply Templates</b-button>
        </router-link>

        <add-permission-component :item_id=final_item_id :item_model=final_item_model> </add-permission-component>

        <!-- Specific permissions -->

        <p v-if="!item_permission_objects.length" class="mt-3">No permissions have been set yet.</p>

        <edit-permission-component v-for="permission in item_permission_objects" v-bind:key="permission.pk"
            :permission=permission :item_id=final_item_id :item_model=final_item_model class="mt-3">
        </edit-permission-component>

        <error-component :message=error_message></error-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import EditPermissionComponent from '../permissions/EditPermissionComponent'
import AddPermissionComponent from '../permissions/AddPermissionComponent'


export default {

    props: ['item_id', 'item_model', 'item_name'],
    components: { ErrorComponent, EditPermissionComponent, AddPermissionComponent },
    store,
    data: function() {
        return {
            error_message: ''
        }
    },
    created: function () {
        var alt_target = this.final_item_model + "_" + this.final_item_id
        this.checkPermissions({permissions: {"apply_template": {alt_target:alt_target} } })
            .catch(error => {  this.error_message = error; console.log(error) })
        this.getPermissionsForItem({ item_id: this.final_item_id, item_model: this.final_item_model })
            .catch(error => {  this.error_message = error })
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        ...Vuex.mapGetters(['permissionsForItem']),
        final_item_id: function() {
            return (typeof this.item_id === "undefined") ? store.state.group_pk : this.item_id },
        final_item_model: function() {
            return (typeof this.item_model === "undefined") ? 'group' : this.item_model },
        final_item_name: function() {
            return (typeof this.item_name === "undefined") ? store.state.group_name : this.item_name },
        title_string: function() {
            return "Permissions for " + this.final_item_name
        },
        item_key: function() {
            return this.final_item_id + "_" + this.final_item_model
        },
        modal_id: function() {
            return "item_permission_modal" + "_" + this.item_key
        },
        item_permission_objects: function() {
            return this.permissionsForItem(this.item_key)
        },
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getPermissionsForItem']),
    }

}

</script>