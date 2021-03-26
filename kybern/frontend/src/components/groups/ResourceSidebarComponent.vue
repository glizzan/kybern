<template>

    <span>

        <div v-for="{ display, model, items } in resources" v-bind:key=model class="mb-4">

            <h5 class="font-weight-bold">

                {{ display }}

                <router-link v-if="model == 'simplelist'" :to="{ name: 'add-new-list'}">
                    <b-button v-if="user_permissions.add_list" variant="light"
                        class="btn-sm ml-3" id="new_list_button">+ add new</b-button>
                </router-link>

                <router-link v-if="model == 'forum'" :to="{ name: 'add-new-forum'}">
                    <b-button v-if="user_permissions.add_forum" variant="light"
                        class="btn-sm ml-3" id="new_forum_button">+ add new</b-button>
                </router-link>

            </h5>

            <b-list-group>

                <b-list-group-item v-for="item in items" v-bind:key=item.pk
                    :active="(item.pk == highlight_pk && model == highlight_model) ? true : false">

                    <router-link :to="get_router_ref(model, item)">
                        {{ item.name }}
                    </router-link>

                </b-list-group-item>
            </b-list-group>

        </div>
    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'


export default {

    props: ['highlight_model', 'highlight_pk'],
    created (){
        if (this.lists.length == 0) { this.getLists() }
        if (this.forums.length == 0) { this.getForumData() }
        this.checkPermissions({permissions: {"add_forum": null, "add_list": null}})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            lists: state => state.simplelists.lists,
            forums: state => state.forums.forums,
            user_permissions: state => state.permissions.current_user_permissions,
        }),
        resources: function() {

            return [
                { display: "Forums", model: "forum", items: this.forums },
                { display: "Lists", model: "simplelist", items: this.lists }
            ]
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getLists', 'getForumData']),
        get_router_ref(model, item) {
            if (model == "simplelist") {
                return { name: "list-detail", params: {list_id: item.pk}}
            }
            if (model == "forum") {
                return { name: "forum-detail", params: {forum_id: item.pk}}
            }
        }
    }
}

</script>

<style scoped>

    .list-group-item a {
        color: #17a2b8;
    }

    .list-group-item.active {
        z-index: 2;
        color: #fff;
        background-color: #17a2b8;
        border-color: #17a2b8;
    }

    .list-group-item.active a {
        color: white;
    }

</style>