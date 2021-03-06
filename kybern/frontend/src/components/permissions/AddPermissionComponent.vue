<template>

    <span>

        <error-component :message=error_message></error-component>

            <div v-if="!permission_selected" class="my-3">

                <b>Select permission to add</b>
                <vue-multiselect v-model="permission_selected" :options="permission_options_to_use" :allow-empty="true"
                :close-on-select="true" placeholder="Select permission" label="text" track-by="value" :max-height="200"
                name="permission_select" group-values="permissions" group-label="section">
                </vue-multiselect>

            </div>

            <div v-else>

                <!-- If a role was not passed in, that means we need to ask the user for what roles and
                    actors should be given this permission. -->
                <span v-if="!role_to_edit" class="mb-3">
                    <p class="mt-3 font-weight-bold">Give people this permission</p>

                    <!-- copied & pasted from 'role_and_actor_fields_include' -->

                        <span class="text-left">

                            <span v-if="anyone_can_take_permission">
                                Anyone can take the action described by this permission.
                                <span v-if="user_permissions.give_anyone_permission">
                                    You can remove the permission from anyone, and give it to the previous roles and/or actors specified.
                                    <b-button variant="outline-secondary" size="sm" @click="toggle_anyone('disable')">
                                        Remove from anyone</b-button>
                                </span>
                            </span>

                            <span v-else>
                                Currently, only the roles and actors below have this permission.
                                <span v-if="user_permissions.remove_anyone_from_permission">
                                    You can give permission to everyone.
                                    <b-button variant="outline-secondary" size="sm" @click="toggle_anyone('enable')">
                                        Give to everyone</b-button></p>
                                </span>
                            </span>

                        </span>

                        <span v-if="!anyone_can_take_permission" class="text-left">

                            <!-- Should be a choice field populated by current roles -->
                            <div class="input-group mb-3 permissionrolefield">

                                Roles who have this permission

                                <vue-multiselect v-model=permission_roles_selected :multiple=true :options=rolesAsOptions :allow-empty="true"
                                    :close-on-select="true" placeholder="Select roles" label="name" track-by="name" name="permission_role_select"
                                    :disabled="permission_exists && !(user_permissions.add_role_to_permission || user_permissions.remove_role_from_permission)">
                                </vue-multiselect>

                            </div>

                            <!-- Should be a multiselect field populated by current members -->
                            <div class="input-group mb-3 permissionactorfield">

                                Actors who have this permission

                                <vue-multiselect v-model=permission_actors_selected :multiple=true :options=groupMembersAsOptions :allow-empty="true"
                                    :close-on-select="true" placeholder="Select actors" label="name" track-by="pk" name="permission_actor_select"
                                    :disabled="permission_exists && !(user_permissions.add_actor_to_permission || user_permissions.remove_actor_from_permission)">
                                </vue-multiselect>

                            </div>

                        </span>

                <!-- end copy & paste -->

                </span>

                <action-response-component :response=add_permission_response></action-response-component>

                <b-button size="sm" class="mt-3" @click="add_permission()" id="save_permission_button">
                    Save permission</b-button>

                <b-button size="sm" class="mt-3" @click="clearState()" id="discard_permission_button">
                    Discard</b-button>

            </div>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import ErrorComponent from '../utils/ErrorComponent'
import { ConfiguredFieldsMixin, PermissionGroupMixin } from '../utils/Mixins'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['default_selection', 'role_to_edit', 'item_id', 'item_model'],  // item_model is required
    components: { "vue-multiselect": Multiselect, ErrorComponent, ActionResponseComponent },
    mixins: [ConfiguredFieldsMixin, PermissionGroupMixin],
    store,
    data: function() {
        return {
            permission_exists: false,
            permission_selected: '',
            error_message: '',
            add_permission_response: null,
            permission_roles_selected: [],
            permission_actors_selected: [],
            anyone_can_take_permission: false
        }
    },
    created () {
        if (this.default_selection) {
            this.permission_selected = this.get_full_selection(this.default_selection)
        }
        var alt_target = this.item_model + "_" + this.item_id
        this.checkPermissions({permissions: {add_permission: {alt_target:alt_target}}})
        .catch(error => {  this.error_message = error; console.log(error) })
    },
    watch: {
        default_selection: function (val) {
            return this.get_full_selection(val)
        },
        permission_options: function (val) {
            if (this.default_selection) {
                this.permission_selected = this.get_full_selection(this.default_selection)
            }

        }
    },
    computed: {
        ...Vuex.mapState({
            permissions: state => state.permissions.permissions,
            permission_options: state => state.permissions.permission_options,
            user_permissions: state => state.permissions.current_user_permissions
            }),
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions', 'getPermissionConfigurationFields',
            'role_to_options', 'user_pk_to_options']),
        item_or_role() {
            if (this.role_to_edit) { return "role"}
            else if (this.item_id && this.item_model) { return "item" }
            return undefined
        },
        item_permission_options() {
            return this.permission_options[this.item_model]
        },
        permission_options_to_use() {
            if (this.role_to_edit) {
                let options = new Map()
                for (let permissioned_object_model in this.permission_options) {
                    this.permission_options[permissioned_object_model].forEach(option => {
                        if (!options.has(option.value)) { options.set(option.value, option) }
                    })
                }
                return this.create_permission_groups(Array.from(options.values()))
            }
            else {
                return this.create_permission_groups(this.item_permission_options) }
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'addPermission']),
        clearState() {
            if (!this.default_selection) { this.permission_selected = '' }
            this.permission_actors_selected = []
            this.permission_roles_selected = []
            this.configuration_fields = []
        },
        get_full_selection(value) {
            for (let group_index in this.permission_options_to_use) {
                for (let permission_index in this.permission_options_to_use[group_index].permissions) {
                    if (this.permission_options_to_use[group_index].permissions[permission_index].value == value) {
                        return this.permission_options_to_use[group_index].permissions[permission_index]
                    }}}
            return undefined
        },
        get_roles() {
            if (this.item_or_role == "role") { return [this.role_to_edit] }
            else if (this.item_or_role == "item") { return this.permission_roles_selected }
        },
        add_permission() {
            this.addPermission({ item_or_role : this.item_or_role, item_id : this.item_id, item_model: this.item_model,
                permission_selected : this.permission_selected.value,
                roles: this.get_roles(), actors: this.permission_actors_selected, anyone: this.anyone })
                .then(response => { this.add_permission_response = response })
        },
        toggle_anyone(enable_or_disable) {
            if (enable_or_disable == "enable") { this.anyone_can_take_permission = true }
            else { this.anyone_can_take_permission = false }
        }
    }

}

</script>


