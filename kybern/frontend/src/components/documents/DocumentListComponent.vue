<template>

    <span>

        <h5 class="pb-3">

            <span class="font-weight-bold">Documents</span>

            <form-button-and-modal v-if="user_permissions.add_document" :item_model="'document'"
                :button_text="'+ add new'" :supplied_variant="'light'" :supplied_classes="'btn-sm ml-3'">
            </form-button-and-modal>

        </h5>

        <b-card-group columns>

            <b-card v-for="({ pk, name, description }, index) in documents" v-bind:key=pk class="bg-white">
                <b-card-text>
                    <div class="font-weight-bold text-info">
                        <router-link :to="{ name: 'document-detail', params: { item_id: pk } }" :id="'link_to_doc_' + index"
                            class="text-info">
                            {{ name }}
                        </router-link>
                    </div>
                    <div class="document-description mt-1">{{ description }}</div>
                </b-card-text>
            </b-card>

        </b-card-group>

        <span v-if="Object.keys(documents).length === 0">There are no documents yet.</span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import FormButtonAndModal from '../utils/FormButtonAndModal'


export default {

    components: { FormButtonAndModal },
    store,
    data: function() {
        return {
        }
    },
    computed: {
        ...Vuex.mapState({
            documents: state => state.documents.documents,
            user_permissions: state => state.permissions.current_user_permissions
        }),
    },
    created () {
        this.getDocuments()
        this.checkPermissions({ permissions: { add_document: null }})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getDocuments'])
    }

}

</script>