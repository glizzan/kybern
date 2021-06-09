<template>

    <b-container class="permission-container">

        <permission-editor-component :mode="'add'"></permission-editor-component>

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
                    <h6>Type of Change</h6>
                    <b-form-select v-model="sectionSelected" :options="section_names"></b-form-select>
                </div>

            </b-col>

            <b-col class="bg-white p-3 table-width">

                <span class="big-text mr-2">All Group Permissions</span>

                <b-icon-plus-circle v-b-tooltip.hover title="Add permission" class="mx-2" variant=warning
                    font-scale=1.5 :id="'add_permission_button'" v-b-modal.add_permission_modal>
                </b-icon-plus-circle>

                <b-icon-grid3x3-gap-fill v-b-tooltip.hover title="Apply templates" variant=warning font-scale=1.5
                    v-if="user_permissions.apply_template" id="apply_templates" class="mr-2"
                    v-b-modal="'apply_template_modal_' + item_model">
                </b-icon-grid3x3-gap-fill>
                <template-modal :scope=item_model :target_id=item_id :target_model=item_model></template-modal>

                <b-iconstack font-scale="1.5" v-b-tooltip.hover title="View advanced permissions" class="mr-2"
                    :id="'advanced_permissions_button'" v-b-modal.advanced_permissions_modal>
                    <b-icon stacked icon="shield-lock-fill" variant="warning"></b-icon>
                    <b-icon stacked icon="star-fill" scale=.5 shift-h="4" shift-v="5" variant="info"></b-icon>
                </b-iconstack>
                <advanced-permissions-modal :item_name=item_name :item_id=item_id :item_model=item_model>
                </advanced-permissions-modal>

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
import PermissionsTableComponent from '../permissions/PermissionsTableComponent'
import TemplateModal from '../templates/TemplateModal'
import AdvancedPermissionsModal from '../permissions/AdvancedPermissionsModal'
import PermissionEditorComponent from '../permissions/PermissionEditorComponent'


export default {

    props: ['permissions', 'item_id', 'item_model', 'item_name'],
    components: { PermissionsTableComponent, TemplateModal, AdvancedPermissionsModal, PermissionEditorComponent },
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
        modal_id: function() { return this.item_key },
        modal: function() { if (this.modal_id) { return this.modal_id } else {return "default" } },
        role_names: function() { return ["", "you", "anyone"].concat(this.allRoleNames) },
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

.table-width {
    max-width: 83%
}

</style>
