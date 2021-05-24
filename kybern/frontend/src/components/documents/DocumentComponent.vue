<template>

    <div v-if="document" class="bg-white p-3">

        <div class="title-and-actions mb-4">

            <span class="h3 font-weight-bold">{{ document.name }}</span>

            <resource-action-icons class="float-right" v-on:delete="delete_document" :item_id=item_id
                :item_model="'document'" :item_name=document.name :edit_permission="user_permissions.edit_document"
                :delete_permission="user_permissions.delete_document"></resource-action-icons>

        </div>

        <action-response-component :response=document_response></action-response-component>

        <p>{{ document.description }}</p>

        <!-- Document-specific actions -->

        <router-link :to="{ name: 'document-full-page', params: {item_id: item_id}}">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="document_fullpage">
                view full page</b-button>
        </router-link>

        <b-button v-if="user_permissions.edit_document && !edit_mode" variant="outline-secondary"
            class="btn-sm mr-2" id="edit_content_start_button" @click="edit_mode=true">edit content</b-button>


        <!-- Content -->

        <DocumentMarkdownComponent v-if="edit_mode" :content=document.content ref="markdown">
            </DocumentMarkdownComponent>
        <div v-else v-html=rendered_content class="pt-4"></div>

        <action-response-component :response=edit_document_content_response></action-response-component>
        <b-button v-if="edit_mode" variant="outline-secondary" class="btn-sm"
            id="edit_document_content_button" @click="edit_content">save edits</b-button>

        <b-button v-if="edit_mode" variant="outline-secondary" class="btn-sm"
            id="discard_content_edits" @click="edit_mode=false">discard</b-button>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import marked from 'marked'
import { UtilityMixin } from '../utils/Mixins'
import DocumentMarkdownComponent from '../documents/DocumentMarkdownComponent'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import ResourceActionIcons from '../utils/ResourceActionIcons'


export default {

    props: ['item_id'],
    store,
    components: {DocumentMarkdownComponent, ActionResponseComponent, ResourceActionIcons },
    mixins: [UtilityMixin],
    data: function() {
            return {
                error_message: null,
                edit_mode: false,
                new_name: "",
                new_description: "",
                document_response: null,
                edit_document_content_response: null
            }
        },
    created (){
        if (!this.document) { this.getDocuments() }
        var alt_target = "document_" + this.item_id
        this.checkPermissions({
            permissions:
                {edit_document: {alt_target : alt_target},
                delete_document: {alt_target : alt_target}}
        }).catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({user_permissions: state => state.permissions.current_user_permissions}),
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
        ...Vuex.mapActions(['checkPermissions', 'getDocuments', 'deleteDocument', 'editDocument']),
        edit_content(field) {
            this.editDocument({pk: this.item_id, content: this.$refs.markdown.current_content })
            .then(response => {
                if (response.data.action_status == "implemented") { this.edit_mode = false }
                else { this.edit_document_content_response = response }
            })
        },
        delete_document() {
            this.deleteDocument({ document_pk: this.item_id })
            .then(response => {
                if (response.data.action_status == "implemented") { this.$router.push({name: 'home'}) }
                else { this.document_response = response }
            })
        }
    }

}

</script>