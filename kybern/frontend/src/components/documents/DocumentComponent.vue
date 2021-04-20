<template>

    <div v-if="document" class="bg-white p-3">

        <h3 class="mt-3">{{ document.name }}</h3>
        <p>{{ document.description }}</p>

        <router-link :to="{ name: 'edit-document', params: { document_id: document_id } }"
                v-if="user_permissions.edit_document">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="edit_document_button">
                edit document info</b-button>
        </router-link>

        <b-button v-if="user_permissions.edit_document && !edit_mode" variant="outline-secondary"
            class="btn-sm mr-2" id="edit_content_start_button" @click="edit_mode=true">edit content</b-button>

        <b-button v-if="user_permissions.delete_document" variant="outline-secondary" class="btn-sm mr-2"
            id="delete_document_button" @click="delete_document(document_id)">delete document</b-button>

        <router-link :to="{ name: 'action-history', params: {item_id: document_id, item_model: 'document',
            item_name: document.name }}">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="document_history_button">
                document history</b-button>
        </router-link>

        <b-button variant="outline-secondary" id="document_permissions_button" v-b-modal.item_permissions_modal
            class="btn-sm mr-2">document permissions</b-button>
        <item-permissions-modal :item_id=document_id :item_model="'document'" :item_name=document.name>
        </item-permissions-modal>

        <router-link :to="{ name: 'document-full-page', params: {document_id: document_id}}">
            <b-button variant="outline-secondary" class="btn-sm mr-2" id="document_fullpage">
                view full page</b-button>
        </router-link>

        <error-component :message="error_message"></error-component>

        <DocumentMarkdownComponent v-if="edit_mode" :content=document.content ref="markdown">
            </DocumentMarkdownComponent>
        <div v-else v-html=rendered_content class="pt-4"></div>

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
import ErrorComponent from '../utils/ErrorComponent'
import ItemPermissionsModal from '../permissions/ItemPermissionsModal'
import DocumentMarkdownComponent from '../documents/DocumentMarkdownComponent'


export default {

    props: ['document_id'],
    store,
    components: { ErrorComponent, ItemPermissionsModal, DocumentMarkdownComponent },
    mixins: [UtilityMixin],
    data: function() {
            return {
                error_message: null,
                edit_mode: false,
                new_name: "",
                new_description: ""
            }
        },
    created (){
        if (!this.document) { this.getDocuments() }
        var alt_target = "document_" + this.document_id
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
            return this.getDocumentData(this.document_id)
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
            this.editDocument({document_pk: this.document_id, content: this.$refs.markdown.current_content })
            .then(response => { this.edit_mode = false })
            .catch(error => {  this.error_message = error })
        },
        delete_document() {
            this.deleteDocument({ document_pk: this.document_id })
            .then(response => { console.log(response); this.$router.push({name: 'home'}) })
            .catch(error => {  this.error_message = error })
        }
    }

}

</script>