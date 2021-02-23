<template>

    <span>

        <h4 class="text-secondary pb-3">Lists

        <router-link :to="{ name: 'add-new-list'}" v-if="user_permissions.add_list">
            <b-button variant="outline-secondary"
                class="btn-sm ml-3" id="new_list_button">+ add new</b-button>
        </router-link>
        </h4>

        <router-link v-for="({ pk, name, description, rows }, index) in lists" v-bind:key=pk
                :to="{ name: 'list-detail', params: { list_id: pk } }" :id="'link_to_list_' + index">
            <b-card v-bind:key=pk class="bg-light text-info border-secondary mb-3">
                <b-card-title>{{ name }}<span class="text-dark ml-2"><small>
                    {{ rows.length }} items</small></span></b-card-title>
                <p class="mb-1 text-secondary list-description"> {{ description }} </p>
            </b-card>
        </router-link>

        <span v-if="Object.keys(lists).length === 0">There are no lists yet.</span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    store,
    data: function() {
        return {
        }
    },
    computed: {
        ...Vuex.mapState({
            lists: state => state.simplelists.lists,
            user_permissions: state => state.permissions.current_user_permissions,
            group_name: state => state.group_name
        }),
    },
    created () {
        this.getLists()
        this.checkPermissions({ permissions: { add_list: null }})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getLists'])
    }

}

</script>