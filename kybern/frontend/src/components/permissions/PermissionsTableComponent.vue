<template>

    <b-table small sticky-header="390px" no-border-collapse responsive
        :items="restructured_permissions" :fields="fields"
        :filter=filter_data :filter-function=filter_function>

        <template #cell(condition)="data">
            <span v-if=data.item.condition>True</span>
        </template>

        <template #cell(change_name)="data">
            <div class="text-nowrap">
                <b-icon-info-circle-fill v-b-tooltip.hover :title="data.item.display" class="mr-2" font-scale=".8">
                </b-icon-info-circle-fill>
                <small>{{ data.item.change_name }}</small>
            </div>
        </template>

        <template #cell(target)="data">
            <div class="text-nowrap">
                <small>{{ data.item.target }}</small>
            </div>
        </template>

        <!-- Default display for cell, displays true-false as checks/xs-->
        <template #cell()="data">
            <span v-if="data.value.has_perm != undefined">
                <b-icon-check-circle-fill v-if="data.value.has_perm == true" variant="success">
                </b-icon-check-circle-fill>
                <b-icon-x v-if="data.value.has_perm == false" variant="danger">
                </b-icon-x>
                <b-icon-question-diamond v-if="data.value.has_perm && data.value.more_info"
                    v-b-tooltip="{ title: data.value.more_info, delay: 0 }">
                </b-icon-question-diamond>
            </span>
            <span v-else>
                {{ data.value }}
            </span>
        </template>

    </b-table>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    props: ['permissions', 'filter_data'],
    store,
    data: function() {
        return {
            prepend_constant_fields: [
                {
                    key: 'change_name',
                    label: 'Change',
                    sortable: true,
                    stickyColumn: true
                },
                {
                    key: 'target',
                    label: 'Target',
                    sortable: true
                },
                {
                    key: 'you',
                    label: 'You',
                    sortable: true
                }
            ],
            append_constant_fields: [
                {
                    key: 'anyone',
                    label: 'Anyone',
                    class: 'text-center'
                }
            ],
            error_message: ''
        }
    },
    computed: {
        ...Vuex.mapGetters(['allRoleNames', 'rolesForMember']),
        ...Vuex.mapState({ owner_condition: state => state.permissions.owner_condition,
                           governor_condition: state => state.permissions.governor_condition,
                           user_pk: state => state.user_pk }),
        fields: function() {
            if (this.permissions) {
                var custom_role_fields = []
                this.allRoleNames.forEach(
                    role_name => custom_role_fields.push({key: role_name, sortable: false, class: 'text-center'}));
                return this.prepend_constant_fields.concat(custom_role_fields.concat(this.append_constant_fields))
            } else {
                return this.constant_fields
            }
        },
        restructured_permissions: function() {
            return this.get_restructured_permissions(this.permissions, this.allRoleNames)
        }
    },
    methods: {
        get_restructured_permissions: function(permissions, roles) {

            var restructured_permissions = {}
            var roles_user_is_in = this.rolesForMember(this.user_pk)

            for (let perm_index in permissions) {

                let permission = permissions[perm_index]
                let key = permission.change_name + permission.target
                let more_info = permission.condition ? permission.condition.how_to_pass_overall : null

                // if permission already in map, add info to "more info" string and skip to next
                if (key in restructured_permissions) {

                    let match = restructured_permissions[key]

                    Object.entries(match).forEach(([key, value]) => {
                        if (key != "owners" && key != "governors") {
                            if (value.more_info && more_info) {
                                value.more_info = value.more_info + " OR " + more_info
                            }
                        }
                    });

                    continue
                }

                // get basic data for row
                let new_dict = {
                    change_name: permission.change_name,
                    foundational: permission.is_foundational,
                    section: permission.section,
                    display: permission.display,
                    target: permission.target,
                    anyone: {has_perm: permission.anyone, more_info: more_info}
                }

                // get permission data for roles
                var vue_data = this
                roles.forEach(function(role_name) {
                    let resp = {has_perm: false}
                    if (permission.roles.includes(role_name)) { resp = {has_perm: true, more_info: more_info}}
                    if (role_name == "owners" && permission.owner_permission) {
                        resp = {has_perm: true}
                        if (vue_data.owner_condition) { resp["more_info"] = vue_data.owner_condition.how_to_pass_overall }
                    }
                    if (role_name == "governors" && permission.governor_permission) {
                        resp = {has_perm: true}
                        if (vue_data.governor_condition) { resp["more_info"] = vue_data.governor_condition.how_to_pass_overall }
                    }
                    new_dict[role_name] = resp
                })

                // get permission data for logged in user
                var userperm = {has_perm: false, more_info: null}

                if (permission.actors.includes(this.user_pk)) { userperm = this.update_perm(userperm, true, more_info) }
                if (permission.anyone) { userperm = this.update_perm(userperm, true, more_info) }
                roles_user_is_in.forEach(function(role_name){
                    if (new_dict[role_name]["has_perm"]) {
                        if (role_name == "owners") {
                            var owner_info = vue_data.owner_condition ? vue_data.owner_condition.how_to_pass_overall : null
                            userperm = vue_data.update_perm(userperm, true, owner_info)
                        } else if (role_name == "governors") {
                            var gov_info = vue_data.governor_condition ? vue_data.governor_condition.how_to_pass_overall : null
                            userperm = vue_data.update_perm(userperm, true, gov_info)
                        } else {
                            userperm = vue_data.update_perm(userperm, true, more_info)
                        }
                    }
                })
                new_dict["you"] = userperm

                restructured_permissions[key] = new_dict
            }

            return Object.values(restructured_permissions)
        },
        update_perm(userperm, has_perm, more_info) {
            console.log(userperm, has_perm, more_info)
            if (!has_perm) { return userperm }
            if (!userperm.has_perm) { return {has_perm: has_perm, more_info: more_info} }
            // if we have an existing permission and a new permsision, determine what info to give
            if (userperm.more_info && more_info) {
                return {has_perm: true, more_info: userperm.more_info + " OR " + more_info}
            } else {
                return {has_perm: true, more_info: null}  // if either of the perms is null, use that
            }
        },
        filter_function(row_data, filter_data) {

            if (Object.keys(filter_data).includes("searchString")) {
                var obj_string = Object.values(row_data).reduce(function (accumulator, element) {
                    return accumulator ? accumulator + " " + element : element
                },"");
                if (!obj_string.includes(filter_data["searchString"])) { return false }
            }

            if (Object.keys(filter_data).includes("roleSelected")) {
                if (!row_data[filter_data["roleSelected"]]["has_perm"]) { return false }
            }

            if (Object.keys(filter_data).includes("targetSelected")) {
                if (row_data["target"] != filter_data["targetSelected"]) { return false }
            }

            if (Object.keys(filter_data).includes("sectionSelected")) {
                if (row_data["section"] != filter_data["sectionSelected"]) { return false }
            }

            return true
        }
    }

}

</script>