<template>

    <span>

        <error-component :message=error_message></error-component>

        <!-- Display existing permission -->
        <b-button-group :id=pair_element_id class="my-2">
            <b-button class="rounded-left btn-sm" variant="light">
                <span class="permission-display" :id="'display_' + pair_element_id">{{ permission.display }}</span>
                <span v-if="can_edit_permission" v-on:click="edit_permission=true"
                    class="badge badge-light ml-1 edit-permission"  >🖉</span>
                <span v-if="user_permissions.remove_permission" v-on:click="delete_permission()"
                    class="badge badge-light ml-1 delete-permission"  >🗑</span>
            </b-button>

            <b-button class="rounded-right btn-sm">
                <span v-if="permission.condition" :id="'condition_' + pair_element_id + '_existing'">
                    <span>on the condition that {{ permission.condition.how_to_pass_overall }}</span>
                    <router-link v-if=user_permissions.remove_permission_condition
                        :to="{name: 'conditions', params: {conditioned_on: permission.pk, dependency_scope: item_model}}">
                        <span class="badge badge-secondary ml-1 edit-condition" :class="css_name(permission.change_name)">🖉</span>
                    </router-link>
                </span>
                <span v-else :id="'condition_' + pair_element_id">
                    <router-link v-if="user_permissions.add_permission_condition"
                        :to="{name: 'conditions', params: {conditioned_on: permission.pk, dependency_scope: item_model}}">
                    <b-button class="add-condition btn-sm">add condition</b-button></router-link>
                    <span v-else>no condition</span>
                </span>
            </b-button>
        </b-button-group>

        <span v-if="edit_permission">

            <div class="p-3">

                <!-- If a role was not passed in, that means we need to ask the user for what roles and
                actors should be given this permission. -->
                <span v-if="!role_to_edit">
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

                </span>

                <!-- If there are fields to configure -->
                <span v-if="configuration_fields.length > 0">
                    <p class="mt-3 font-weight-bold">Configure your permission</p>
                    <field-component v-for="field in configuration_fields"
                        v-on:field-changed="change_field" :initial_field=field v-bind:key=field.field_name>
                    </field-component>
                </span>

                <div class="block">
                    <b-button size="sm" class="mt-3" @click="update_permission()" id="update_permission_button">
                        Update permission</b-button>

                    <b-button size="sm" class="mt-3" @click="edit_permission=false" id="discard_permission_button">
                        Discard changes</b-button>
                </div>

            </div>

        </span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'
import ErrorComponent from '../utils/ErrorComponent'
import FieldComponent from '../fields/FieldComponent'
import { ConfiguredFieldsMixin } from '../utils/Mixins'


export default {

    props: ['permission', 'role_to_edit', 'item_id', 'item_model'],
    store,
    components: { "vue-multiselect": Multiselect, ErrorComponent, FieldComponent },
    mixins: [ConfiguredFieldsMixin],
    data: function() {
        return {
            permission_exists: true,
            edit_permission: false,
            edit_condition: false,
            configuration_fields: [],
            permission_roles_selected: [],
            permission_actors_selected: [],
            error_message: ''
        }
    },
    created () {
        var alt_target = "permissionsitem_" + this.permission.pk
        this.checkPermissions({permissions: {
            remove_permission: {alt_target:alt_target},
            add_permission_condition: {alt_target:alt_target},
            remove_permission_condition: {alt_target:alt_target},
            add_actor_to_permission: {alt_target:alt_target},
            remove_actor_from_permission: {alt_target:alt_target},
            add_role_to_permission: {alt_target:alt_target},
            remove_role_from_permission: {alt_target:alt_target},
            give_anyone_permission: {alt_target:alt_target},
            remove_anyone_from_permission: {alt_target:alt_target},
            change_configuration_of_permission: {alt_target:alt_target}}
        }).catch(error => {  this.error_message = error; console.log(error) })
    },
    watch: {
        permission: function(val) { this.refresh_permission_data(val) },
        edit_permission: function(edit_permission) {
            if (edit_permission == true) {
                this.refresh_permission_data(this.permission)
            }
        }
    },
    computed: {
        ...Vuex.mapState({
            permissions: state => state.permissions.permissions,
            user_permissions: state => state.permissions.current_user_permissions
        }),
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions', 'getPermissionConfigurationFields',
            'getPermissionConfigurationFieldsWithData', 'role_to_options',
            'user_pk_to_options']),
        anyone_can_take_permission() { return this.permission.anyone },
        item_or_role() {
            if (this.role_to_edit) { return "role"}
            else if (this.item_id && this.item_model) { return "item" }
            return undefined
        },
        pair_element_id() {
            return "permission_element_" + this.permission.pk
        },
        can_edit_permission() {
            if (this.user_permissions.add_actor_to_permission || this.user_permissions.remove_actor_from_permission ||
            this.user_permissions.add_role_to_permission || this.user_permissions.remove_role_from_permission ||
            this.user_permissions.give_anyone_permission || this.user_permissions.remove_anyone_from_permission ||
            this.user_permissions.change_configuration_of_permission) {
                return true
            } else {
                return false
            }
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'removePermission', 'updatePermission', 'toggleAnyone']),
        get_roles() {
            if (this.item_or_role == "role") { return [this.role_to_edit] }
            else if (this.item_or_role == "item") { return this.permission_roles_selected }
        },
        refresh_permission_data(permission) {
            if (permission) {
                this.configuration_fields = Object.values(
                    this.getPermissionConfigurationFieldsWithData(permission.pk))
                if (this.item_id && this.item_model) { // only do this for permission on item
                    this.permission_roles_selected = this.role_to_options(permission.roles)
                    this.permission_actors_selected = this.user_pk_to_options(permission.actors)
                }
            }
        },
        clearState() {
            this.edit_permission = false,
            this.edit_condition = false,
            this.configuration_fields = []
            this.permission_roles_selected = []
            this.permission_actors_selected = []
        },
        css_name(name) { return name.replace(" ", "_") },
        // Vuex actions
        delete_permission() {
            this.removePermission({ permission_id : this.permission.pk, item_id: this.item_id,
                    item_model: this.item_model, item_or_role : this.item_or_role })
            .then(response => { this.clearState() })
            .catch(error => {  this.error_message = error.message  })
        },
        update_permission() {
            this.updatePermission({ permission_id: this.permission.pk,
                configuration : this.configuration_fields, roles: this.get_roles(),
                actors: this.permission_actors_selected
            }).then(response => { this.clearState() })
            .catch(error => {  this.error_message = error })
        },
        toggle_anyone(enable_or_disable) {
            this.toggleAnyone({ permission_id: this.permission.pk,
                                            enable_or_disable: enable_or_disable })
            .catch(error => {  this.error_message = error })
        }
    }

}

</script>