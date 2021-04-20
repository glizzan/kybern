<template>

    <b-modal id="document_modal" :title=title_string size="md" :visible=true hide-footer @hide="$router.go(-1)">

        <b-form-group id="name_form_group" label="Document name:" label-for="document_name">
            <b-form-input id="document_name" name="document_name" v-model="name" required
                placeholder="Please pick a name for your document">
            </b-form-input>
        </b-form-group>

        <b-form-group id="description_form_group" label="Document description:" label-for="document_description">
            <b-form-textarea id="document_description" name="document_description" v-model="description"
                placeholder="Add a description, if you want">
            </b-form-textarea>
        </b-form-group>

        <b-button variant="outline-secondary" class="btn-sm" id="submit_document_button"
            @click="submit_document">submit</b-button>

        <error-component :message=error_message></error-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import { UtilityMixin } from '../utils/Mixins'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['document_id'],
    components: { ErrorComponent },
    store,
    data: function() {
        return {
            name: null,
            description: null,
            error_message: null
        }
    },
    created () {
        if (this.document_id) {
            var document = this.getDocumentData(this.document_id)
            this.name = document.name
            this.description = document.description
        }
    },
    computed: {
        ...Vuex.mapState({documents: state => state.documents.documents}),
        ...Vuex.mapGetters(['getDocumentData']),
        title_string: function() {
            if (this.document_id) {  return "Edit document '" + this.name + "'" }
            else { return "Create a new document" }
        }
    },
    methods: {
        ...Vuex.mapActions(['addDocument', 'editDocument']),
        submit_document() {
            if (this.document_id) {
                this.editDocument({document_pk: this.document_id, name: this.name,
                    description: this.description})
                .then( response => this.$bvModal.hide("document_modal") )
                .catch(error => {  console.log(error), this.error_message = error })
            } else {
                this.addDocument({ name: this.name, description: this.description })
                .then( response => {
                    // hack until we fix the axios call system to return data
                    var id = this.documents[this.documents.length - 1].pk
                    this.$router.push({name: 'document-detail', params: {document_id: id}})
                })
                .catch(error => {  console.log(error), this.error_message = error })
            }
        }
    }

}

</script>