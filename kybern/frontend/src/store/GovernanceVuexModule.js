import Vue from 'vue'


const GovernanceVuexModule = {

    state: {

        // Roles & members
        members: [],    // [ pk, pk, pk, pk ]
        roles: [],              // [ { name: role_name, current_members: [pk, pk, pk] } ]
        users: [],              // [ { name: 'username', pk: pk } ]
        current_membership_option: "",         // ie "invite only", "anyone can join"
        membership_config_data: { "permission": null, "condition": null },         // { permission: null, condition: null }

        // Leadership data
        governance_info: "",                    // Text string explaining governance structure
        owners: {actors:[], roles:[]},              // { actors: [pk, pk], roles: ['rolename', 'rolename'] }
        governors: {actors:[], roles:[]},        // { actors: [pk, pk], roles: ['rolename', 'rolename'] }

    },
    getters: {

        memberNames: (state, getters) => {
            return state.members.map(member => { return getters.getUserName(member) })
        },
        roleNames: state => {
            var names = []
            state.roles.forEach(function(item){ names.push(item.name)})
            return names
        },
        allRoleNames: state => {
            var names = ["owners", "governors", "members"]
            state.roles.forEach(function(item){ names.push(item.name)})
            return names
        },
        allRoles: (state, getters) => {
            return [{ name: "members", current_members: state.members }].concat(state.roles)
        },
        rolesAsOptions: (state, getters) => {
            return getters.allRoles.map(role => { return {name: role.name } })
        },
        getUser: (state) => (pk) => {
            return state.users.find(user => user.pk == pk)
        },
        getUserName: (state, getters) => (pk) => {
            return getters.getUser(pk).name
        },
        userInGroup: (state, getters) => (pk) => {
            return state.members.includes(pk)
        },
        membersInRole: (state, getters) => (role_name) => {
            return state.roles.find(role => role.name == role_name).current_members
        },
        rolesForMember: (state, getters) => (user_pk, custom_only) => {

            var roles_user_is_in = []

            if(!user_pk) { console.log("user_pk passed in is undefined"); return roles_user_is_in }

            state.roles.forEach(function(role) {
                if (role.current_members.includes(user_pk)) { roles_user_is_in.push(role.name) }
            })

            if (!custom_only) {

                if (getters.userInGroup(user_pk)) { roles_user_is_in.push("members") }

                if (state.owners.actors.includes(user_pk)) {
                    roles_user_is_in.push("owners")
                } else {
                    let matched_roles = state.owners.roles.filter(role => roles_user_is_in.includes(role));
                    if (matched_roles.length > 1) { roles_user_is_in.push("owners") }
                }

                if (state.owners.actors.includes(user_pk)) {
                    roles_user_is_in.push("governors")
                } else {
                    let matched_roles = state.governors.roles.filter(role => roles_user_is_in.includes(role));
                    if (matched_roles.length > 1) { roles_user_is_in.push("governors") }
                }
            }
            return roles_user_is_in
        },
        role_to_options: (state, getters) => (role_list) => {
            if (!role_list) { return [] }
            if (!Array.isArray(role_list)) { role_list = [ role_list ]}
            return role_list.map(role => { return  { name: role } })
        },
        user_pk_to_options: (state, getters) => (pk_list) => {
            if (pk_list) {
                return pk_list.map(pk => { return  { pk: pk, name: getters.getUser(pk).name }  })
            } else {
                return []
            }
        },
        groupMembersAsOptions: (state, getters) => {
            return getters.user_pk_to_options(state.members)
        },
        roleMembersAsOptions: (state, getters) => (role_name) => {
            var role_members = getters.membersInRole(role_name)
            return getters.user_pk_to_options(role_members)
        },
        membersAsOptions: (state, getters) => (role_name) => {
            if (role_name == 'members') {  return getters.groupMembersAsOptions  }
            else {  return getters.roleMembersAsOptions(role_name)  }
        },
        nonmembersAsOptions: (state, getters) => {
            return state.users.filter(user => state.members.indexOf(user.pk) == -1 )
        },
        leadershipAsOptions: (state, getters) => {
            return {
                owner_role_options: state.owners.roles.map(role => { return {name: role } }),
                owner_actor_options: getters.user_pk_to_options(state.owners.actors),
                governor_role_options: state.governors.roles.map(role => { return {name: role } }),
                governor_actor_options: getters.user_pk_to_options(state.governors.actors)
            }
        }
    },
    mutations: {
        SET_CURRENT_USER_AS_ONLY_GROUP_MEMBER (state, data) {
            Vue.set(state, "users", data.users)
            Vue.set(state, "members", [data.user_pk])
        },
        SET_USERS (state, data) {
            Vue.set(state, 'users', data.users);
        },
        SET_ROLES (state, data) {
            Vue.set(state, 'roles', data.roles);
        },
        SET_LEADERS(state, data) {
            Vue.set(state, "owners", data.owners);
            Vue.set(state, "governors", data.governors)
        },
        SET_GOVERNANCE_INFO(state, data) {
            Vue.set(state, "governance_info", data.governance_info)
        },
        ADD_ROLE (state, data) {
            var role_exists = state.roles.find(role => role.name == data.role_name)
            if (!role_exists) {
                state.roles.push({ name: data.role_name, current_members: [] })
            }
        },
        REMOVE_ROLE (state, data) {
            var index = state.roles.findIndex(role => role.name == data.role_name)
            if (index > -1) { state.roles.splice(index, 1)}
        },
        ADD_MEMBERS (state, data ) {
            for (let index in data.user_pks) {
                var user_pk = data.user_pks[index]
                var index_of_member = state.members.indexOf(user_pk)
                if (index_of_member == -1) { state.members.push(user_pk) }
            }
        },
        REMOVE_MEMBERS (state, data) {
            for (let index in data.user_pks) {
                var user_pk = data.user_pks[index]
                var index_of_member = state.members.indexOf(user_pk)
                if (index_of_member > -1) {  state.members.splice(index_of_member, 1) }
            }
        },
        ADD_USERS_TO_ROLE (state, data) {
            var role = state.roles.find(role => role.name == data.role_name)
            for (let index in data.user_pks) {
                var user_pk = data.user_pks[index]
                var index_of_pk = role.current_members.indexOf(user_pk)
                if (index_of_pk == -1) { role.current_members.push(user_pk) }
            }
        },
        REMOVE_USERS_FROM_ROLE (state, data) {
            var role = state.roles.find(role => role.name == data.role_name)
            for (let index in data.user_pks) {
                var user_pk = data.user_pks[index]
                var index_of_pk = role.current_members.indexOf(user_pk)
                if (index_of_pk > -1) { role.current_members.splice(index_of_pk, 1) }
            }
        },
        REMOVE_USERS_FROM_ALL_ROLES (state, data) {
            state.roles.forEach( function(role){
                data.user_pks.forEach( function(user_pk) {
                    var index_of_user_in_role = role.current_members.indexOf(user_pk)
                    if (index_of_user_in_role > -1 ) { role.current_members.splice(index_of_user_in_role, 1) }
                })
            })
        },
        ADD_OWNERS (state, data) {
            data.roles_to_add.forEach(function(role){
                if (!state.owners.roles.includes(role)) {
                    state.owners.roles.push(role) }
            })
            data.actors_to_add.forEach(function(actor){
                if (!state.owners.actors.includes(actor)) {
                    state.owners.actors.push(actor) }
            })
        },
        REMOVE_OWNERS (state, data) {
            data.roles_to_remove.forEach(function(role){
                var index = state.owners.roles.indexOf(role)
                if (index > -1) { state.owners.roles.splice(index, 1)}
            })
            data.actors_to_remove.forEach(function(actor){
                var index = state.owners.actors.indexOf(actor)
                if (index > -1) { state.owners.actors.splice(index, 1)}
            })
        },
        ADD_GOVERNORS (state, data) {
            data.roles_to_add.forEach(function(role){
                if (!state.governors.roles.includes(role)) { state.governors.roles.push(role) }
            })
            data.actors_to_add.forEach(function(actor){
                if (!state.governors.actors.includes(actor)) { state.governors.actors.push(actor) }
            })
        },
        REMOVE_GOVERNORS (state, data) {
            data.roles_to_remove.forEach(function(role){
                var index = state.governors.roles.indexOf(role)
                if (index > -1) { state.governors.roles.splice(index, 1)}
            })
            data.actors_to_remove.forEach(function(actor){
                var index = state.governors.actors.indexOf(actor)
                if (index > -1) { state.governors.actors.splice(index, 1)}
            })
        },
        SET_MEMBERSHIP_OPTION_SELECTED (state, data) {
            state.current_membership_option = data.selection
        },
        SET_MEMBERSHIP_CONFIG_DATA (state, data) {
            Vue.set(state.membership_config_data, "condition", data.condition_data)
            Vue.set(state.membership_config_data, "permission", data.permission_data)
        }

    },

    actions: {
        initialize_members_with_current_user ({ commit, state, dispatch, getters}, payload) {
            commit('SET_CURRENT_USER_AS_ONLY_GROUP_MEMBER', {users: [payload.user], user_pk: payload.user.pk})
        },
        async getGovernanceData ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('get_governance_data')
            var implementationCallback = (response) => {
                commit('SET_USERS', { users: response.data.governance_data.users })
                commit('SET_ROLES', { roles: response.data.governance_data.roles })
                commit('SET_LEADERS', { owners: response.data.governance_data.owners,
                                        governors: response.data.governance_data.governors })
                commit('ADD_MEMBERS', { user_pks: response.data.governance_data.current_members })
                commit('SET_GOVERNANCE_INFO', { governance_info: response.data.governance_data.governance_info })
            }
            return dispatch('getAPIcall', { url: url, implementationCallback: implementationCallback})
        },
        async addMembers ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('add_members')
            var params = { user_pks : payload.user_pks }
            var implementationCallback = () => { commit('ADD_MEMBERS', { user_pks: payload.user_pks }) }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async removeMembers ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('remove_members')
            var params = { user_pks : payload.user_pks }
            var implementationCallback = () => {
                commit('REMOVE_USERS_FROM_ALL_ROLES', { user_pks: payload.user_pks })
                commit('REMOVE_MEMBERS', { user_pks: payload.user_pks })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addUsersToRole ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('add_people_to_role')
            var params = { role_name : payload.role_name, user_pks: payload.user_pks }
            var implementationCallback = () => { commit('ADD_USERS_TO_ROLE',
                { role_name : payload.role_name, user_pks: payload.user_pks }) }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async  removeUsersFromRole ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('remove_people_from_role')
            var params = { role_name : payload.role_name, user_pks: payload.user_pks }
            var implementationCallback = () => { commit('REMOVE_USERS_FROM_ROLE',
                { role_name : payload.role_name, user_pks: payload.user_pks }) }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async addRole ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('take_action')
            var params = { action_name: "add_role_to_community", role_name: payload.role_name }
            var implementationCallback = () => { commit('ADD_ROLE', { role_name: payload.role_name }) }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        // async addRole ({ commit, state, dispatch, getters}, payload) {
        //     var url = await getters.url_lookup('add_role_to_group')
        //     var params = { role_name: payload.role_name }
        //     var implementationCallback = () => { commit('ADD_ROLE', { role_name: payload.role_name }) }
        //     return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        // },
        async removeRole ({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('remove_role_from_group')
            var params = { role_name: payload.role_name }
            var implementationCallback = () => { commit('REMOVE_ROLE', { role_name: payload.role_name }) }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async updateOwners({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('update_owners')
            var params = { owner_roles: payload.roles, owner_actors: payload.actors }
            var implementationCallback = () => {
                var roles_to_add = payload.roles.filter(x => !state.owners.roles.includes(x))
                var actors_to_add = payload.actors.filter(x => !state.owners.actors.includes(x))
                var roles_to_remove = state.owners.roles.filter(x => !payload.roles.includes(x))
                var actors_to_remove = state.owners.actors.filter(x => !payload.actors.includes(x))
                commit('ADD_OWNERS', { roles_to_add: roles_to_add, actors_to_add: actors_to_add })
                commit('REMOVE_OWNERS', { roles_to_remove: roles_to_remove, actors_to_remove: actors_to_remove })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        },
        async updateGovernors({ commit, state, dispatch, getters}, payload) {
            var url = await getters.url_lookup('update_governors')
            var params = { governor_roles: payload.roles, governor_actors: payload.actors }
            var implementationCallback = () => {
                var roles_to_add = payload.roles.filter(x => !state.governors.roles.includes(x))
                var actors_to_add = payload.actors.filter(x => !state.governors.actors.includes(x))
                var roles_to_remove = state.governors.roles.filter(x => !payload.roles.includes(x))
                var actors_to_remove = state.governors.actors.filter(x => !payload.actors.includes(x))
                commit('ADD_GOVERNORS', { roles_to_add: roles_to_add, actors_to_add: actors_to_add })
                commit('REMOVE_GOVERNORS', { roles_to_remove: roles_to_remove, actors_to_remove: actors_to_remove })
            }
            return dispatch('actionAPIcall', { url: url, params: params, implementationCallback: implementationCallback})
        }
     }

}

export default GovernanceVuexModule