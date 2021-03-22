<template>
    <span>

        <navbar-component :user_name=user_name :signed_in=signed_in></navbar-component>

        <b-container fluid>

            <b-row class="bg-white">
                <b-col><router-view name="sidebar"></router-view></b-col>
            </b-row>

            <b-row>
                <b-col cols="12" class="p-4"><router-view name="main"></router-view></b-col>
            </b-row>

            <router-view name="modal"></router-view>

        </b-container>

    </span>

</template>

<script>

let initialState = JSON.parse(window.__INITIAL_STATE__);

import store from '../store'
import NavbarComponent from '../components/utils/NavbarComponent'

export default {

    components: { NavbarComponent },
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


<style>
body {
  /* background-color: lightgray; */
  background-color: #ededed;
}
</style>
