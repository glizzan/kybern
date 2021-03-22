<template>

    <span>

        <h5 class="pb-3">
            <span class="font-weight-bold">Forums</span>
            <router-link :to="{ name: 'add-new-forum'}">
                <b-button v-if="user_permissions.add_forum" variant="light"
                    class="btn-sm ml-3" id="new_forum_button">+ add new</b-button>
            </router-link>
        </h5>

        <b-card-group columns>

            <b-card v-for="{ pk, name, description } in processed_forums" v-bind:key=pk class="bg-white">
                <b-card-text>
                    <div class="forum-link font-weight-bold text-info">
                        <router-link :to="{ name: 'forum-detail', params: {forum_id: pk}}" class="text-info">
                            {{ name }}</router-link>
                    </div>
                    <div class="forum-description mt-1">{{ description }}</div>
                </b-card-text>
            </b-card>

        </b-card-group>

    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    store,
    computed: {
        ...Vuex.mapState({
            forums: state => state.forums.forums,
            user_permissions: state => state.permissions.current_user_permissions,
            group_name: state => state.group_name
        }),
        processed_forums: function() {
            var processed_forums = []
            for (let index in this.forums) {
                if (this.forums[index].special == "Gov") {
                    processed_forums.unshift(this.forums[index])
                }
                else { processed_forums.push(this.forums[index]) }
            }
            return processed_forums
        }
    },
    created () {
        this.checkPermissions({permissions: {"add_forum": null}})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions'])
    }

}

</script>

<style scoped>

    .card-deck .card {
        max-width: 5px;
    }

</style>


