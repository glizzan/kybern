<template>

    <div v-if="document" class="bg-white p-3">

        <div class="title-and-actions mb-4">

            <span class="h3 font-weight-bold">{{ document.name }}</span>

            <!-- GAH, hidden on  -->

            <resource-action-icons class="float-right" v-on:delete="delete_document" :item_id=item_id
                :item_model="'document'" :item_name=document.name :response=delete_response>
            </resource-action-icons>

        </div>

        <p>{{ document.description }}</p>

        <!-- Document-specific actions -->

        <router-link :to="{ name: 'document-full-page', params: {item_id: item_id}}">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="document_fullpage">
                view full page</b-button>
        </router-link>

        <b-button v-if="!edit_mode" variant="outline-secondary" class="btn-sm mr-2"
            id="edit_content_start_button" @click="edit_mode=true">edit content</b-button>

        <!-- Content -->

        <DocumentMarkdownComponent v-if="edit_mode" :content=document.content ref="markdown">
            </DocumentMarkdownComponent>
        <div v-else v-html=rendered_content class="pt-4"></div>


        <div class="my-2">

            <take-action-component v-if="edit_mode" v-on:take-action="edit_content" :response=edit_content_response
                :verb="'save edits'" :action_name="'edit_document'" v-on:close-modal="modal_closed">
            </take-action-component>

            <b-button v-if="edit_mode" variant="outline-secondary" id="discard_content_edits" class="ml-2"
                @click="edit_mode=false">discard</b-button>
        </div>


    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import marked from 'marked'
import { UtilityMixin } from '../utils/Mixins'
import DocumentMarkdownComponent from '../documents/DocumentMarkdownComponent'
import ResourceActionIcons from '../utils/ResourceActionIcons'
import TakeActionComponent from '../actions/TakeActionComponent'


export default {

    props: ['item_id'],
    store,
    components: {DocumentMarkdownComponent, TakeActionComponent, ResourceActionIcons },
    mixins: [UtilityMixin],
    data: function() {
            return {
                error_message: null,
                edit_mode: false,
                new_name: "",
                new_description: "",
                delete_response: null,
                edit_content_response: null
            }
        },
    created (){
        if (!this.document) { this.getDocuments() }
    },
    computed: {
        ...Vuex.mapGetters(['getDocumentData']),
        document: function() {
            return this.getDocumentData(this.item_id)
        },
        rendered_content: function() {
            if (this.document) {
                return marked(this.document.content, { sanitize: true });
            }
            return null
        }
    },
    methods: {
        ...Vuex.mapActions(['getDocuments', 'deleteDocument', 'editDocument']),
        modal_closed() {
            if (this.edit_content_response && this.edit_content_response.data.action_status == "implemented") {
                this.edit_mode = false
            }
        },
        edit_content(extra_data) {
            this.editDocument({pk: this.item_id, content: this.$refs.markdown.current_content, extra_data: extra_data })
            .then(response => { this.edit_content_response = response })
        },
        delete_document(extra_data) {
            this.deleteDocument({ pk: this.item_id, extra_data: extra_data })
            .then(response => {
                if (response.data.action_status == "implemented") { this.$router.push({name: 'home'}) }
                else { this.delete_response = response }
            })
        }
    }

}

</script>