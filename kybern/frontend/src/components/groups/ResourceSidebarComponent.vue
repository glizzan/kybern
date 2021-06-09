<template>

    <span>

        <div v-for="{ display, model, items } in resources" v-bind:key=model class="mb-4">

            <h5 class="font-weight-bold">

                {{ display }}

                <form-button-and-modal v-if="model == 'simplelist'" :item_model="'list'" :button_text="'+ add new'"
                    :supplied_variant="'light'" :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>

                <form-button-and-modal v-if="model == 'forum'" :item_model="'forum'" :button_text="'+ add new'"
                    :supplied_variant="'light'" :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>

                <form-button-and-modal v-if="model == 'document'" :item_model="'document'" :button_text="'+ add new'"
                    :supplied_variant="'light'" :supplied_classes="'btn-sm ml-3'"></form-button-and-modal>

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
    },
    computed: {
        ...Vuex.mapState({
            lists: state => state.simplelists.lists,
            forums: state => state.forums.forums,
            documents: state => state.documents.documents,
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
        ...Vuex.mapActions(['getLists', 'getForums', 'getDocuments']),
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