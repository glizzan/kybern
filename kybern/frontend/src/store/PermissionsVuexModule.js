import Vue from 'vue'


const PermissionsVuexModule = {

    state: {

        // Permission & condition options
        permission_options: {},
            // [ { value: x , text: x } ]
        permission_configuration_options: {},
            // { permission_type: { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }
        condition_options: [],
            // [ { value: x , text: x } ]
        condition_configuration_options: {},
            // { condition_type: { fieldname: { display: x, type: x, required: x, value: x, field_name: x } }
        dependent_field_options: [],

        // Permission data (loaded opportunistically)
        permissions: {},                // { int(pk) : { name: x, display: x, change_type: x } }
        permission_overrides: {},       // { item_pk + "_" + item_model: { foundational: enabled, governing: disabled } }

        // Logged in user permissions
        current_user_permissions: {},    // { 'permission_shortname': boolean, 'permission_shortname': boolean }

        // Permissions associated with roles and items
        role_permissions: {},           // { role_name: [pk, pk, pk], role_name: [pk, pk, pk] }
        item_permissions: {},           // { item_pk + "_" + item_model: [pk, pk, pk] }

        // Governance conditions
        owner_condition: null,
        governor_condition: null

    },

    getters: {
        get_permission_given_pk: (state, getters) => (pk, as_dict) => {
            var permission = state.permissions[pk]
            if (!permission) { console.log("No permission found for ", pk); return }
            if (as_dict) {
                return { [pk] : state.permissions[pk] }
            } else {
                permission["pk"] = pk
                return permission
            }
        },
        get_list_of_permissions_given_pks: (state, getters) => (pk_list) => {
            var matching_permissions = []
            for (let index in pk_list) {
                matching_permissions.push(getters.get_permission_given_pk(pk_list[index]))
            }
            return matching_permissions
        },
        permissionsForRole: (state, getters) => (role_name) => {
            var permission_pks = state.role_permissions[role_name]
            return getters.get_list_of_permissions_given_pks(permission_pks)
        },
        permissionsForItem: (state, getters) => (item_key) => {
            var permission_pks = state.item_permissions[item_key]
            return getters.get_list_of_permissions_given_pks(permission_pks)
        },
        getPermissionConfigurationFields: (state, getters) => (permission_type) => {
            // JSON stringify + parse create a new copy of the fields so we don't accidentally mutate state by reference
            return JSON.parse( JSON.stringify( state.permission_configuration_options[permission_type] ))
        },
        getConditionConfigurationFields: (state, getters) => (condition_type) => {
            for (let key in state.condition_configuration_options) {
                if (key.toLowerCase() == condition_type.toLowerCase()) {
                    var configuration = state.condition_configuration_options[key]
                    break
                }
            }
            // JSON stringify + parse create a new copy of the fields so we don't accidentally mutate state by reference
            return JSON.parse( JSON.stringify( configuration ))
        },
        fix_permission_field_values: (state, getters) => (field) => {
            if (typeof(field.value) == "string" && field.value.indexOf("{{") > -1) { return field }  // leave replaced field as is
            if (field.type == "RoleField" || field.type == "RoleListField") {
                field.value = getters.role_to_options(field.value)
            } else if (field.type == "ActorField" || field.type == "ActorListField") {
                field.value = getters.user_pk_to_options(field.value)
            }
            return field
        },
        mapPermissionDataToFields: (state, getters) => (fields, existing_data) => {
            // Loops through data-less configuration fields looking for existing data to override
            // default values.
            var new_fields = Object.keys(fields).map(function(field_name) {
                if (existing_data[field_name]) {
                    fields[field_name].value = existing_data[field_name]
                    fields[field_name] = getters.fix_permission_field_values(fields[field_name])
                    return fields[field_name]
                } else {
                    return fields[field_name]
                }
            });
            return new_fields
        },
        getPermissionConditionConfigurationFieldsWithData: (state, getters) => (permission_id, element_id) => {
            var fields = state.permissions[permission_id]["condition"][element_id]["fields"]
            for (let field_index in fields) {
                fields[field_index] = getters.fix_permission_field_values(fields[field_index])
            }
            return fields
        },
        getLeadershipConditionConfigurationFieldsWithData: (state, getters) => (leadership_type, element_id) => {
            if (leadership_type == "owner") { fields = state.owner_condition[element_id]["fields"] }
            else if (leadership_type == "governor") { fields = state.governor_condition[element_id]["fields"] }
            for (let field_index in fields) {
                fields[field_index] = getters.fix_permission_field_values(fields[field_index])
            }
            return fields
        },
        getPermissionConfigurationFieldsWithData: (state, getters) => (permission_id) => {
            var permission = state.permissions[permission_id]
            var field_options = getters.getPermissionConfigurationFields(permission.change_type)
            return getters.mapPermissionDataToFields(field_options, permission["fields"])
        },
        getFoundationalForItem: (state, getters) => (item_key) => {
            if (state.permission_overrides[item_key]) {
                return state.permission_overrides[item_key].foundational
            }
        },
        getGoverningForItem: (state, getters) => (item_key) => {
            if (state.permission_overrides[item_key]) {
                return state.permission_overrides[item_key].governing
            }
        }
    },

    mutations: {

        // set options

        SET_PERMISSION_OPTIONS (state, data) {
            Vue.set(state, "permission_options", data.options)
        },
        SET_PERMISSION_CONFIGURATION_OPTIONS (state, data) {
            Vue.set(state, "permission_configuration_options", data.options)
        },
        SET_CONDITION_OPTIONS (state, data) {
            Vue.set(state, "condition_options", data.options)
        },
        SET_CONDITION_CONFIGURATION_OPTIONS (state, data) {
            Vue.set(state, "condition_configuration_options", data.options)
        },
        SET_DEPENDENT_FIELD_OPTIONS (state, data) {
            Vue.set(state, "dependent_field_options", data.options)
        },

        // permissions

        ADD_OR_UPDATE_PERMISSION (state, data) {
            Vue.set(state.permissions, data.pk, data.data) // { name: x, display: x, change_type: x } }
        },
        ADD_PERMISSION_TO_ROLE (state, data ) {
            var permission_index = state.role_permissions[data.role].indexOf(data.pk)
            if (permission_index == -1) { state.role_permissions[data.role].push(data.pk) }
        },
        REMOVE_PERMISSION_FROM_ROLES (state, data ) {
            for (let role in state.role_permissions) {
                var permission_index = state.role_permissions[role].indexOf(data.pk)
                if (permission_index > -1) {
                    state.role_permissions[role].splice(permission_index, 1)
                }
            }
        },
        UPDATE_ROLE_WITH_PERMISSION (state, data) {
            for (let index in data.permission.roles) {
                var role = data.permission.roles[index]
                if (!state.role_permissions[role]) {
                    Vue.set(state.role_permissions, role, [data.permission.pk])
                } else {
                    var permission_index = state.role_permissions[role].indexOf(data.permission.pk)
                    if (permission_index < 0) { state.role_permissions[role].push(data.permission.pk) }
                }
            }
        },
        REPLACE_ROLE_PERMISSIONS (state, data) {
            Vue.set(state.role_permissions, data.role, data.pks)
        },
        DELETE_PERMISSION (state, data) {
            Vue.delete(state.permissions, data.pk);
        },
        REPLACE_ITEM_PERMISSIONS (state, data) {
            var item_key = data.item_id + "_" + data.item_model
            Vue.set(state.item_permissions, item_key, data.pks)
        },
        ADD_PERMISSION_TO_ITEM (state, data ) {
            var item_key = data.item_id + "_" + data.item_model
            var permission_index = state.item_permissions[item_key].indexOf(data.permission_pk)
            if (permission_index == -1) { state.item_permissions[item_key].push(data.permission_pk) }
        },
        REMOVE_PERMISSION_FROM_ITEM (state, data) {
            var item_key = data.item_id + "_" + data.item_model
            var permission_index = state.item_permissions[item_key].indexOf(data.pk)
            if (permission_index > -1) { state.item_permissions[item_key].splice(permission_index, 1) }
        },
        ADD_OR_UPDATE_CURRENT_USER_PERMISSIONS (state, data) {
            for (let permission in data.user_permissions) {
                Vue.set(state.current_user_permissions, permission, data.user_permissions[permission])
            }
        },
        ADD_OR_UPDATE_PERMISSION_OVERRIDE_DATA (state, data) {
            var item_key = data.item_id + "_" + data.item_model
            Vue.set(state.permission_overrides, item_key, {
                "foundational": data.foundational, "governing": data.governing
            })
        },

        // Condition Mutations

        SET_PERMISSION_CONDITION (state, data) {
            Vue.set(state.permissions[data.pk], "condition", data.condition_data)
        },
        SET_LEADERSHIP_CONDITION (state, data) {
            if (data.leadership_type == "owner") {
                Vue.set(state, "owner_condition", data.condition_data)
            } else if (data.leadership_type == "governor") {
                Vue.set(state, "governor_condition", data.condition_data)
            }
        }

    },

    actions: {

        // initialize data

        async getPermissionData ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('get_permission_data')
            var implementationCallback = (response) => {
                commit('SET_PERMISSION_OPTIONS', { options: response.data.permission_options })
                commit('SET_PERMISSION_CONFIGURATION_OPTIONS', { options: response.data.permission_configuration_options })
                commit('SET_CONDITION_OPTIONS', { options: response.data.condition_options })
                commit('SET_CONDITION_CONFIGURATION_OPTIONS', { options: response.data.condition_configuration_options })
                commit('SET_DEPENDENT_FIELD_OPTIONS', { options: response.data.dependent_field_options })
                commit('SET_LEADERSHIP_CONDITION', { 'leadership_type': "owner",
                        condition_data: response.data.owner_condition })
                commit('SET_LEADERSHIP_CONDITION', { 'leadership_type': "governor",
                        condition_data: response.data.governor_condition })
            }
            return dispatch('getAPIcall', { url: url, implementationCallback: implementationCallback})
        },

        // 'fetch only if necessary'

        fetchMissingPermission ({ commit, state, getters, dispatch }, payload) {
            return new Promise((resolve, reject) => {

                var pk = parseInt(payload.pk)
                if (isNaN(pk)) { reject("pk " + payload.pk + " is not a number") }

                var permission = getters.get_permission_given_pk(pk)
                if (permission) { resolve(permission) }

                dispatch('getPermission', {permission_pk: pk})
                .then(response => resolve(getters.get_permission_given_pk(pk)))
                .catch(error => reject("Couldn't find permission matching " + payload.pk))

            })
        },

        // Permission Actions

        async addPermission ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('add_permission')
            var params = { item_or_role: payload.item_or_role, item_id: payload.item_id,
                item_model: payload.item_model, permission_type : payload.permission_selected,
                permission_roles : payload.roles, permission_actors : payload.actors,
                permission_configuration : payload.configuration }

            var implementationCallback = (response) => {
                var pk = response.data.permission.pk
                var permission_data = response.data.permission.permission_data[0]
                commit('ADD_OR_UPDATE_PERMISSION', { pk : pk, data : permission_data })
                if (payload.item_or_role == "role") {
                    commit('ADD_PERMISSION_TO_ROLE', { pk : pk, role: payload.roles })
                } else {
                    commit('ADD_PERMISSION_TO_ITEM', { permission_pk: pk, item_id: payload.item_id,
                        item_model: payload.item_model })
                }
            }

            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async updatePermission ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('update_permission')
            var params = { permission_id : payload.permission_id, permission_roles : payload.roles,
                permission_actors : payload.actors, permission_configuration : payload.configuration }
            var implementationCallback = (response) => {
                pk = response.data.permission.pk
                permission_data = response.data.permission.permission_data[0]
                commit('ADD_OR_UPDATE_PERMISSION', { pk : pk, data : permission_data })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async removePermission ({ commit, dispatch, getters }, payload) {
            var url = await getters.url_lookup('delete_permission')
            var params = { permission_id : payload.permission_id }
            var implementationCallback = (response) => {

                commit('REMOVE_PERMISSION_FROM_ROLES', { pk: response.data.removed_permission_pk } )

                if (payload.item_or_role == "item") {
                    commit('REMOVE_PERMISSION_FROM_ITEM', { pk: response.data.removed_permission_pk,
                    item_id : payload.item_id, item_model: payload.item_model })
                } else {
                    // TODO: if removed from role interface, may still be set on item - check for
                    // permission pk in group
                }

                commit('DELETE_PERMISSION', { pk: response.data.removed_permission_pk })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        // Condition Actions

        async addCondition ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('add_condition')
            var params = { condition_type: payload.condition_type, permission_or_leadership: payload.permission_or_leadership,
                target_permission_id: payload.permission_id, leadership_type: payload.leadership_type,
                combined_condition_data : payload.combined_condition_data }

            var implementationCallback = (response) => {
                if (response.data.permission_or_leadership == "permission") {
                    commit('SET_PERMISSION_CONDITION', { pk: response.data.target_permission_id,
                        condition_data: response.data.condition_info })
                } else {
                    commit('SET_LEADERSHIP_CONDITION', { 'leadership_type': response.data.leadership_type,
                        condition_data: response.data.condition_info })
                }
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback })
        },

        async editCondition ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('edit_condition')
            var params = { permission_or_leadership: payload.permission_or_leadership, element_id: payload.element_id,
                target_permission_id: payload.permission_id, leadership_type: payload.leadership_type,
                combined_condition_data : payload.combined_condition_data }

            var implementationCallback = (response) => {
                if (response.data.permission_or_leadership == "permission") {
                    commit('SET_PERMISSION_CONDITION', { pk: response.data.target_permission_id,
                        condition_data: response.data.condition_info })
                } else {
                    commit('SET_LEADERSHIP_CONDITION', { 'leadership_type': response.data.leadership_type,
                        condition_data: response.data.condition_info })
                }
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback })
        },

        async removeCondition ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('remove_condition')
            var params = { permission_or_leadership: payload.permission_or_leadership,
                target_permission_id : payload.permission_id, leadership_type: payload.leadership_type,
                element_id: payload.element_id }
            var implementationCallback = (response) => {
                if (response.data.permission_or_leadership == "permission") {
                    commit('SET_PERMISSION_CONDITION', { pk: response.data.target_permission_id,
                        condition_data: response.data.condition_info })
                } else {
                    commit('SET_LEADERSHIP_CONDITION', { 'leadership_type': response.data.leadership_type,
                        condition_data: response.data.condition_info })
                }
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        // Misc other actions
        async getPermission({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('get_permission')
            var params = { permission_pk: payload.permission_pk }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_PERMISSION', { pk : payload.permission_pk, data : response.data.permission_data })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async getPermissionsForItem({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_permissions')
            var params = { item_id: payload.item_id, item_model: payload.item_model }
            var implementationCallback = (response) => {
                commit('REPLACE_ITEM_PERMISSIONS', { item_id: response.data.item_id,
                                                     item_model: response.data.item_model,
                                                     pks: response.data.permission_pks })
                for (let key in response.data.permissions) {
                    commit('ADD_OR_UPDATE_PERMISSION', { pk : key, data : response.data.permissions[key] })
                    commit('UPDATE_ROLE_WITH_PERMISSION', { permission: response.data.permissions[key] })
                }
                commit('ADD_OR_UPDATE_PERMISSION_OVERRIDE_DATA', {
                    item_id: response.data.item_id,
                    item_model: response.data.item_model,
                    foundational: response.data.foundational,
                    governing: response.data.governing
                })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async changePermissionOverride ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('change_item_permission_override')
            var params = { item_id: payload.item_id, item_model: payload.item_model,
                enable_or_disable: payload.enable_or_disable, governing_or_foundational: payload.governing_or_foundational }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_PERMISSION_OVERRIDE_DATA', {
                    item_id: response.data.item_id,
                    item_model: response.data.item_model,
                    foundational: response.data.foundational,
                    governing: response.data.governing
                })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async toggleAnyone ({ commit, getters, dispatch }, payload) {
            var url = await getters.url_lookup('toggle_anyone')
            var params = { permission_id : payload.permission_id, enable_or_disable: payload.enable_or_disable }
            var implementationCallback = (response) => {
                var pk = response.data.permission.pk
                var permission_data = response.data.permission.permission_data[0]
                commit('ADD_OR_UPDATE_PERMISSION', { pk : pk, data : permission_data })
            }
        return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async checkPermissions ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('check_permissions')
            var params = { permissions: payload.permissions }
            var implementationCallback = (response) => {
                commit('ADD_OR_UPDATE_CURRENT_USER_PERMISSIONS', { user_permissions: response.data.user_permissions })
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },

        async refreshRoleData ({ commit, state, dispatch, getters }, payload) {
            var url = await getters.url_lookup('get_data_for_role')
            var params = { role_name : payload.role }
            var implementationCallback = (response) => {
                commit('REPLACE_ROLE_PERMISSIONS', { role: payload.role, pks: response.data.role_permissions })
                for (let key in response.data.permissions) {
                    commit('ADD_OR_UPDATE_PERMISSION', { pk : key, data : response.data.permissions[key] })
                }
            }
            return dispatch('getAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
    }
}

export default PermissionsVuexModule