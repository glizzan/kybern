<template>

    <span v-if="user">

        <div>
            <b-card :title=title body-class="text-center" header-tag="nav">
                <template v-slot:header>
                <b-nav card-header tabs>
                    <b-nav-item link-classes="text-info" @click="tab='roles'; " v-bind:active="tab=='roles'">
                        Roles</b-nav-item>
                </b-nav>
                </template>

                <b-card-text>

                    <div v-if="tab=='roles'" class="my-3 mx-5">

                        <h4 class="font-weight-bold">Roles</h4>

                        <error-component :message=error_message></error-component>

                        <p class="text-left mt-4 mb-2">Roles {{user.name}} is in:</p>

                        <b-container>
                            <b-row v-for="role in in_roles" class="my-2" v-bind:key=role.name>
                                <b-col cols="9" class="text-left">
                                    <span class="font-weight-bold">{{role.name}}</span>
                                    <span class="ml-2 text-muted">permissions: {{ to_list(role.permissions) }}</span>
                                </b-col>
                                <b-col>
                                    <b-button class="btn-sm ml-3 float-right " variant="outline-secondary"
                                        @click="remove_role(role)">remove from role</b-button>
                                </b-col>
                            </b-row>
                        </b-container>

                        <p class="text-left mt-4 mb-2">Roles {{user.name}} is not part of:</p>

                        <b-container>
                            <b-row v-for="role in out_roles" class=my-2 v-bind:key=role.name>
                                <b-col cols="9" class="text-left">
                                    <span class="font-weight-bold">{{role.name}}</span>
                                    <span class="ml-2 text-muted">permissions: {{ to_list(role.permissions) }}</span>
                                </b-col>
                                <b-col>
                                    <b-button class="btn-sm ml-3 float-right " variant="outline-secondary"
                                        @click="add_role(role)">add to role</b-button>
                                </b-col>
                            </b-row>
                        </b-container>

                    </div>

                </b-card-text>

            </b-card>
        </div>
    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['user_pk'],
    components: { ErrorComponent },
    store,
    data: function() {
        return {
            tab: 'roles',
            error_message: ''
        }
    },
    created: function () {
        this.getGovernanceData()
        this.getPermissionsForItem({ item_id: this.group_pk, item_model: 'group' })
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            user_permissions: state => state.permissions.current_user_permissions,
            group_name: state => state.group_name,
            group_pk: state => state.group_pk,
            roles: state => state.governance.roles
        }),
        ...Vuex.mapGetters(['permissionsForItem', 'getUser', 'permissionsForRole']),
        title: function() {
            if (this.user) {
                return this.user.name + "'s privileges in " + this.group_name
            } else {
                return "user " + self.user_pk + "'s privileges in " + this.group_name
            }
        },
        user: function() {
            return this.getUser(this.user_pk)
        },
        in_roles: function() {
            return this.user_annotated_roles.filter(role => role.user_is_member == true)
        },
        out_roles: function() {
            return this.user_annotated_roles.filter(role => role.user_is_member == false)
        },
        user_annotated_roles: function() {
            var user_annotated_roles = []
            for (let index in this.roles) {
                var role = this.roles[index]
                role["user_is_member"] = (role.current_members.indexOf(parseInt(this.user_pk)) > -1) ? true : false
                role["permissions"] = this.permissionsForRole(role.name)
                user_annotated_roles.push(role)
            }
            return this.roles
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getPermissionsForItem', 'addUsersToRole', 'removeUsersFromRole', 'getGovernanceData']),
        to_list(list) {
            var names = Array.from(list, item => item.name)
            return names.join(", ")
        },
        add_role(role) {
            this.addUsersToRole({ role_name: role.name, user_pks: [parseInt(this.user_pk)] })
            .catch(error => {  this.error_message = error })
        },
        remove_role(role) {
            this.removeUsersFromRole({ role_name: role.name, user_pks: [parseInt(this.user_pk)] })
            .catch(error => {  this.error_message = error })
        }
    }

}

</script>