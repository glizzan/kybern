<template>
    <span>

        <div id="navbarVueApp">
        <b-navbar toggleable="lg" type="dark" variant="info">
            <!-- Left aligned nav items -->
            <b-navbar-brand href="/">Kybern</b-navbar-brand>
            <b-navbar-toggle target="nav-collapse"></b-navbar-toggle>
            <b-collapse id="nav-collapse" is-nav>
            <b-navbar-nav>
            <b-nav-item href="/groups/list">Groups</b-nav-item>
            <b-nav-item href="#" disabled>Contacts</b-nav-item>
            <b-nav-item href="#" disabled>Notifications</b-nav-item>
            </b-navbar-nav>
            <!-- Right aligned nav items -->
            <b-navbar-nav class="ml-auto">

                <!-- If user is logged in -->
                <b-nav-item-dropdown right v-if="signed_in">
                    <!-- Using 'button-content' slot -->
                    <template v-slot:button-content><em>{{ user_name }}</em></template>
                    <b-dropdown-item href="/profile">Your Profile</b-dropdown-item>
                    <b-dropdown-item href="/logout">Sign Out</b-dropdown-item>
                </b-nav-item-dropdown>

                <!-- If not logged in, show login page. -->
                <b-nav-item v-else href="/login" >Sign In</b-nav-item>

            </b-navbar-nav>
            </b-collapse>
        </b-navbar>
        </div>

        <div class="container">
            <div class="mt-5">
                <div class="row">

                    <div class="col-3">
                        <router-view name="sidebar"></router-view>
                    </div>

                    <div class="col-9">
                        <router-view name="main"></router-view>
                    </div>

                    <router-view name="modal"></router-view>

                </div>

            </div>
        </div>

    </span>

</template>

<script>

let initialState = JSON.parse(window.__INITIAL_STATE__);

import store from '../store'

export default {

    store,
    data: function() {
          return {
            user_name: initialState.user_name,
            signed_in: initialState.is_authenticated
          }
    },
    methods: {
    ...Vuex.mapActions(['initialize_group_data', 'getPermissionData', 'getGovernanceData', 'getForumData']),
    },
    created: function () {
        this.initialize_group_data({urls: initialState.urls, group_pk: initialState.group_pk,
                                    group_name: initialState.group_name, user_pk: initialState.user_pk,
                                    group_description: initialState.group_description,
                                    user_name: initialState.user_name })
        this.getPermissionData()
        this.getGovernanceData()
        this.getForumData()
    }

}

</script>
