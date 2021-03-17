<template>

    <b-container class="permission-container">

        <b-row no-gutters>

            <b-col cols=2 class="py-3 pr-3">

                <h5 class="font-weight-bold mb-4">Filters</h5>

                <div class="my-3">
                    <h6>Roles</h6>
                    <b-form-select v-model="roleSelected" :options="role_names"></b-form-select>
                </div>

                <div class="my-3">
                    <h6>Targets</h6>
                    <b-form-select v-model="targetSelected" :options="target_names"></b-form-select>
                </div>

                <div class="my-3">
                    <h6>Types</h6>
                    <b-form-select v-model="sectionSelected" :options="section_names"></b-form-select>
                </div>

            </b-col>

            <b-col class="bg-white p-3">

                <span class="big-text mr-2">All Group Permissions</span>

                <router-link :to="{ name: 'advanced-permissions', params: { item_id: item_id, item_model: item_model} }">

                    <b-iconstack font-scale="1.5" v-b-tooltip.hover title="View advanced permissions" class="mx-2">
                    <b-icon stacked icon="shield-lock-fill" variant="warning"></b-icon>
                    <b-icon stacked icon="star-fill" scale=.5 shift-h="4" shift-v="5" variant="info"></b-icon>
                    </b-iconstack>

                </router-link>

                <router-link :to="{ name: 'item-templates', params: {scope: item_model, target_id: item_id, target_model: item_model} }"
                             v-if="user_permissions.apply_template" id="apply_templates" class="mr-2">
                    <b-icon-grid3x3-gap-fill v-b-tooltip.hover title="Apply templates" variant=info font-scale=1.5>
                    </b-icon-grid3x3-gap-fill>
                </router-link>

                <b-iconstack font-scale="1.5" v-b-tooltip.hover title="Add permission" class="mr-2"
                    :id="'add_permission_button_' + modal" v-b-modal="'add_permission_modal_'  + modal">
                <b-icon stacked icon="shield-lock-fill" variant="warning"></b-icon>
                <b-icon stacked icon="plus" variant="info" shift-h="-3" shift-v="-4"></b-icon>
                </b-iconstack>

                <add-permission-modal-component :item_name=item_name :item_id=item_id :item_model=item_model
                    :modal_id="'add_permission_modal_'  + modal">
                </add-permission-modal-component>

                <b-iconstack font-scale="1.5" v-b-tooltip.hover title="Edit permissions" class="mr-2"
                    :id="'edit_permissions_button_' + modal" v-b-modal="'edit_permissions_modal_'  + modal">
                    <b-icon stacked icon="shield-lock-fill" variant="warning"></b-icon>
                    <b-icon stacked icon="pencil-fill" scale=.5 variant="info" shift-h="-3" shift-v="-4"></b-icon>
                </b-iconstack>

                <edit-permissions-modal-component :permissions=permissions :item_name=item_name
                    :item_id=item_id :item_model=item_model :modal_id="'edit_permissions_modal_'  + modal">
                </edit-permissions-modal-component>

                <b-form-input id="search_permissions" v-model="permissionSearchString" type="search"
                    placeholder="Search permissions"></b-form-input>

                <permissions-table-component :permissions=permissions class="my-3" :filter_data=filter_data>
                </permissions-table-component>

            </b-col>

        </b-row>

    </b-container>

</template>

<script>

// note - this should always be a child component on GroupPermissions or NonGroupPermissions

import Vuex from 'vuex'
import store from '../../store'
import AddPermissionModalComponent from '../permissions/AddPermissionModalComponent'
import EditPermissionsModalComponent from '../permissions/EditPermissionsModalComponent'
import PermissionsTableComponent from '../permissions/PermissionsTableComponent'


export default {

    props: ['permissions', 'item_id', 'item_model', 'item_name'],
    components: { AddPermissionModalComponent, EditPermissionsModalComponent, PermissionsTableComponent },
    store,
    data: function() {
        return {
            permissionSearchString: '',
            roleSelected: null,
            targetSelected: null,
            sectionSelected: null
        }
    },
    created: function () {
        var alt_target = this.item_model + "_" + this.item_id
        this.checkPermissions({permissions: {"apply_template": {alt_target:alt_target} } })
            .catch(error => { console.log(error) })
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        ...Vuex.mapGetters(['allRoleNames']),
        title_string: function() { return "Permissions for " + this.item_name },
        item_key: function() { return this.item_id + "_" + this.item_model },
        modal_id: function() { return "item_permission_modal" + "_" + this.item_key },
        modal: function() { if (this.modal_id) { return this.modal_id } else {return "default" } },
        role_names: function() { return [""].concat(this.allRoleNames) },
        target_names: function() { return this.get_array("target") },
        section_names: function() { return this.get_array("section")},
        filter_data: function() {
            var data = {}
            if (this.permissionSearchString) { data["searchString"] = this.permissionSearchString }
            if (this.roleSelected) { data["roleSelected"] = this.roleSelected }
            if (this.targetSelected) { data["targetSelected"] = this.targetSelected }
            if (this.sectionSelected) { data["sectionSelected"] = this.sectionSelected }
            return data
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions']),
        get_array(attr) {
            var attr_names = [""]
            this.permissions.forEach((permission) => {
                if(!attr_names.includes(permission[attr])) { attr_names.push(permission[attr]) }
            })
            return attr_names
        }
    }

}

</script>

<style scoped>

.permission-container {
    max-width: 100%;
}

.big-text {
    font-size: 150%;
    font-weight: bold;
}

#search_permissions {
    display: inline;
    width: 50%;
    float: right;
}

</style>
