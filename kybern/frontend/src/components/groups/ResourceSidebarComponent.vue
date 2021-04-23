<template>

    <span>

        <div v-for="{ display, model, items } in resources" v-bind:key=model class="mb-4">

            <h5 class="font-weight-bold">

                {{ display }}

                <router-link v-if="model == 'simplelist'" :to="{ name: 'add-new-list'}">
                    <b-button v-if="user_permissions.add_list" variant="light"
                        class="btn-sm ml-3" id="add_list_default_button">+ add new</b-button>
                </router-link>

                <form-button-and-modal v-if="model == 'forum' && user_permissions.add_forum"
                    :item_model="'forum'" :button_text="'+ add new'" :supplied_variant="'light'"
                    :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>

                <form-button-and-modal v-if="model == 'document' && user_permissions.add_document"
                    :item_model="'document'" :button_text="'+ add new'" :supplied_variant="'light'"
                    :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>

            </h5>

            <b-list-group>

                <b-list-group-item v-for="item in items" v-bind:key=item.pk
                    :active="(item.pk == highlight_pk && model == highlight_model) ? true : false">

                    <router-link :to="get_router_ref(model, item)">
                        {{ item.name }}
                    </router-link>

                </b-list-group-item>
            </b-list-group>

            <span v-if="Object.keys(items).length === 0">There are no {{display.toLowerCase()}} yet.</span>

        </div>
    </span>

</template>


<script>

import Vuex from 'vuex'
import store from '../../store'
// import DocumentFormComponent from '../documents/DocumentFormComponent'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { FormButtonAndModal },
    props: ['highlight_model', 'highlight_pk'],
    created (){
        if (this.lists.length == 0) { this.getLists() }
        if (this.forums.length == 0) { this.getForums() }
        if (this.documents.length == 0) { this.getDocuments() }
        this.checkPermissions({permissions: {"add_forum": null, "add_list": null, "add_document": null}})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({
            lists: state => state.simplelists.lists,
            forums: state => state.forums.forums,
            documents: state => state.documents.documents,
            user_permissions: state => state.permissions.current_user_permissions,
        }),
        resources: function() {

            return [
                { display: "Forums", model: "forum", items: this.forums },
                { display: "Lists", model: "simplelist", items: this.lists },
                { display: "Documents", model: "document", items: this.documents }
            ]
        }
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getLists', 'getForums', 'getDocuments']),
        get_router_ref(model, item) {
            if (model == "simplelist") {
                return { name: "list-detail", params: {list_id: item.pk}}
            }
            if (model == "forum") {
                return { name: "forum-detail", params: {item_id: item.pk}}
            }
            if (model == "document") {
                return { name: "document-detail", params: {item_id: item.pk}}
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