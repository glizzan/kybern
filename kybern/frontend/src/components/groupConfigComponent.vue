// Layout component with subcomponents for editing group, viewing governance, permissions
// and history

<template>

    <span>

        <div class="card">
            <h5 class="card-header">[[ group_name ]]</h5>
            <div class="card-body">
                <p class="card-text">[[ group_description ]]</p>
            </div>
        </div>

        <error-component :message=error_message></error-component>

        <b-button v-if="user_permissions.join_group" block class="mt-3" id="join_group_button" @click="join_group()"
            variant="outline-secondary">join group</b-button>

        <b-button v-if="user_permissions.leave_group" block class="mt-3" id="leave_group_button" @click="leave_group()"
            variant="outline-secondary">leave group</b-button>

        <router-link :to="{ name: 'edit-group'}">
            <b-button id="edit_group_button" block class="mt-3"
                :variant="$route.meta.highlight === 'edit-group' ? 'secondary' : 'outline-secondary'">
                edit group</b-button>
        </router-link>

        <router-link :to="{ name: 'home'}">
            <b-button id="resources_button" block class="mt-3"
                :variant="($route.meta.highlight) ? 'outline-secondary' : 'secondary'">
                resources</b-button>
        </router-link>

        <router-link id="group_history_button" :to="{ name: 'action-history', params: { item_id: 99999,
        item_model: 'group', item_name: group_name }}">
            <b-button block class="mt-3"
                :variant="$route.meta.highlight == 'history' ? 'secondary' : 'outline-secondary'">
                history</b-button>
        </router-link>

        <router-link :to="{ name: 'governance'}">
            <b-button id="governance_button" block class="mt-3"
                :variant="$route.meta.highlight == 'governance' ? 'secondary' : 'outline-secondary'">
                governance</b-button>
        </router-link>

        <router-link class="button" :to="{ name: 'item-permissions', params: { item_id: 99999,
        item_model: 'group', item_name: group_name }}">
            <b-button id="group_permissions_button" block class="mt-3"
                :variant="$route.meta.highlight == 'permissions' ? 'secondary' : 'outline-secondary'">
                permissions</b-button>
        </router-link>

    </span>

</template>

<script>

    // import Vuex from 'vuex'
    import store from '../store'



    export default {
        name: 'group-config-component',
        delimiters: ['[[', ']]'],
        store,
        data: function() {
            return {
                error_message: null,
                user_permissions: {}
            }
        },
        created () {
            // this.checkPermissions({permissions: {"join_group": null, "leave_group": null} })
        },
        computed: {
            // ...Vuex.mapState({
            //     group_name: state => state.group_name,
            //     group_description: state => state.group_description,
            //     user_permissions: state => state.permissions.current_user_permissions
            // })
        },
        methods: {
            // ...Vuex.mapActions(['checkPermissions', 'addMembers', 'removeMembers']),
            // join_group() {
            //     this.addMembers({ user_pks: [99999] }).then(() => window.location.reload())
            //     .catch(error => {  this.error_message = error; console.log(error) })
            // },
            // leave_group() {
            //     this.removeMembers({ user_pks: [99999] }).then(() => window.location.reload())
            //     .catch(error => {  this.error_message = error; console.log(error) })
            // }
        }
    };

</script>