<template>

    <span>

        <b-button :id=button_id :variant=variant :class=classes v-b-modal="modal_id">
            {{ button_text }}</b-button>

        <b-modal :id=modal_id :title=title_string size="lg" hide-footer>

            <field-component v-for="field in configuration_fields" v-bind:key=field.field_name
                :initial_field=field v-on:field-changed="change_field"></field-component>

            <action-response-component class="my-2" :response=action_response></action-response-component>

            <b-button variant="outline-secondary" class="btn-sm" :id="submit_button_id"
                 @click="takeAction">submit</b-button>

        </b-modal>

    </span>

</template>

<script>

// When adding a new model to support, make sure to add their data to fields_dict
// *and* make sure the component is registering the get method in Computed and action method in Methods

var fields_dict = {
    "document": [
        {field_name: "name", label: "Document name:", type: "CharField", required: false, value: null},
        {field_name: "description", label: "Document description:", type: "CharField", required: false, value: null},
    ],
    "forum": [
        {field_name: "name", label: "Forum name:", type: "CharField", required: false, value: null},
        {field_name: "description", label: "Forum description:", type: "CharField", required: false, value: null},
    ],
    "post": [
        {field_name: "title", label: "Post title:", type: "CharField", required: false, value: null},
        {field_name: "content", label: "Post content:", type: "CharField", required: false, value: null},
    ],
    "comment": [
        {field_name: "text", label: "Comment text:", type: "CharField", required: false, value: null},
    ],
    "list": [
        {field_name: "name", label: "List name:", type: "CharField", required: false, value: null},
        {field_name: "description", label: "List description:", type: "CharField", required: false, value: null},
    ]
}

import Vuex from 'vuex'
import store from '../../store'
import { ConfiguredFieldsMixin } from '../utils/Mixins'
import ActionResponseComponent from '../actions/ActionResponseComponent'
import FieldComponent from '../fields/FieldComponent'


export default {

    props: ['item_id', 'item_model', 'button_text', 'supplied_variant', 'supplied_classes', 'supplied_params', 'id_add'],
    components: { ActionResponseComponent, FieldComponent },
    mixins: [ConfiguredFieldsMixin],
    store,
    data: function() {
        return {
            item_instance: null,
            action_response: null,
            configuration_fields: []
        }
    },
    created() {
        this.configuration_fields = JSON.parse( JSON.stringify( fields_dict[this.item_model] ) )
        if (this.item_id) {
            var getMethodName = "get" + this.capitalize(this.item_model) + "Data"
            this.item_instance = this[getMethodName](this.item_id)
        }
    },
    watch: {
        item_instance: function(val) { if (val) { this.initialize_configuration_fields() } }
    },
    computed: {
        ...Vuex.mapGetters(['getDocumentData', 'getForumData', 'getPostData', 'getCommentData', 'getListData']),
        mode: function() { if (this.item_id) { return "edit"}  else { return "add" } },
        to_add: function() { if (this.id_add) { return this.id_add } else { return "default"} },
        id_preface: function() { return this.mode + "_" + this.item_model + "_" + this.to_add },
        button_id: function() { return this.id_preface + "_button" },
        modal_id: function() { return this.id_preface + "_modal" },
        submit_button_id: function() { return this.id_preface + "_submit_button"},
        title_string: function() { return this.capitalize(this.mode) + " " + this.item_model },
        variant: function() {
            if (this.supplied_variant) { return this.supplied_variant } else { return "outline-secondary" }
        },
        classes: function() {
            if (this.supplied_classes) { return this.supplied_classes } else { return "btn-sm mr-2" }
        }
    },
    methods: {
        ...Vuex.mapActions(['addDocument', 'editDocument', 'addForum', 'editForum', 'addPost', 'editPost',
            'addComment', 'editComment', 'addList', 'editList']),
        capitalize(text) { return text.charAt(0).toUpperCase() + text.slice(1) },
        initialize_configuration_fields() {
            if (this.item_instance) {
                for (let i in this.configuration_fields) {
                    let field = this.configuration_fields[i]
                    field["value"] = this.item_instance[field["field_name"]]
                }
            }
        },
        get_params() {
            var params_dict = {}
            if (this.item_id) { params_dict["pk"] = this.item_id }
            if (this.supplied_params) { params_dict = Object.assign({}, params_dict, this.supplied_params) }
            for (let i in this.configuration_fields) {
                let field = this.configuration_fields[i]
                if (field["value"]) {
                    params_dict[field["field_name"]] = field["value"]
                }
            }
            return params_dict
        },
        takeAction() {
            var actionMethodName = this.mode + this.capitalize(this.item_model)
            this[actionMethodName](this.get_params()).then( response => {
                this.action_response = response
                if (this.mode == "add" && response.data.action_status == "implemented" && this.item_model != 'comment') {
                    var params_dict = {item_id: response.data.created_instance.pk}
                    if (this.supplied_params) { params_dict = Object.assign({}, params_dict, this.supplied_params) }
                    this.$router.push({name: this.item_model + '-detail', params: params_dict})
                }
            })
        }
    }

}

</script>


