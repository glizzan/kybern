<template>

    <b-modal size="lg" title="Configure your dependent field" hide-footer :id=modal_id>

        Instead of providing a value now, you can make the value of this field depend on something related,
        for instance the action which is being evaluated by the permission/condition.
        <hr />

        Choose object to depend on:
        <span id="model_options" class="my-3">
            <b-button v-for="model in model_options" v-bind:key=model @click="model_selected=model" class="mr-2"
                :id="'depend_on_model_' + model" :variant="button_variant(model)">{{ model }}</b-button>
        </span>

        <div class="block my-2" v-if="model_selected" id="model_config">
            Select field on {{ model_selected }} (leave blank to use {{ model_selected }} itself):<br />
            <b-form-select v-model="field_selected" :options="field_options" class="dependent-field-select"
                name="dependent-field-select"></b-form-select>
        </div>

        <error-component :message=error_message></error-component>
        <hr />

        <div class="block mt-3">
            <b-button @click="change_dependent_field()" id='save-dependent-field'>save
                <span v-if="model_selected"> '{{model_selected}}<span v-if="field_selected"> {{field_selected}}</span>'</span>
            </b-button>
            <b-button @click="remove_dependent_field()">remove dependent field</b-button>
        </div>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['modal_id', 'field', 'initial_model_selected', 'initial_field_selected'],
    components: { ErrorComponent },
    store,
    data: function() {
        return {
            model_selected: null,
            field_selected: null,
            field_options: [],
            permission: null,
            error_message: null
        }
    },
    inject: ['dependency_scope'],
    created () {
        this.model_selected = this.initial_model_selected
        this.field_selected = this.initial_field_selected
        this.permission = this.$parent.$parent.$parent.$parent.$parent.$parent.permission // Wish provide/inject was working!!
    },
    watch: {
        initial_model_selected: function(val) { this.model_selected = val },
        initial_field_selected: function(val) { this.field_selected = val },
        model_selected: function(val) {
            this.field_options = this.get_field_options(val)
            this.field_selected = null  // always wipe field when model changes
        }
    },
    computed: {
        ...Vuex.mapState({model_and_field_options_unprocessed: state => state.permissions.dependent_field_options }),
        model_options: function () {
            var options = []
            this.permission.dependent_field_options.forEach(option =>{
                options.push(this.replace_generic_models(option))
            })
            return options
        },
        field_option_selected: function() {
            var result = null
            this.field_options.forEach(option =>
                { if (option.text == this.field_selected) { result = option }
            })
            return result
        }
    },
    methods: {
        get_field_options(model_selected) {
            var initial_field_options = this.model_and_field_options_unprocessed[model_selected]
            var final_field_options = []
            // add action change fields
            if (model_selected == "action") {
                this.permission.change_field_options.forEach(option => initial_field_options.push(option))
            }
            // populate options with only matching fields
            initial_field_options.forEach(option => {
                if (this.match_field_types(this.field.type, option.type)) {
                    final_field_options.push(option)
                }
            })
            return final_field_options
        },
        match_field_types: function (source_field_type, field_option_type) {
            var actor_field_names = ["ActorListField", "ActorPKField", "ActorField"]
            var role_field_names = ["RoleListField", "RoleField"]
            if (actor_field_names.indexOf(source_field_type) > -1 && actor_field_names.indexOf(field_option_type) > -1) {
                    return true }
            if (role_field_names.indexOf(source_field_type) > -1 && role_field_names.indexOf(field_option_type) > -1) {
                    return true }
            if (source_field_type ==  field_option_type) { return true }
            return false
        },
        replace_generic_models: function (model) {
            var swaps = {forum : {commented_object: 'post', post: 'commented_object' }}
            if (this.dependency_scope in swaps) {
                if (model in swaps[this.dependency_scope]) {
                    return swaps[this.dependency_scope][model]
                }
            }
            return model
        },
        get_transform_string: function() {
            if (!this.field_selected) { return "" }

            if (this.field.type == "ActorListField") {
                if (this.field_option_selected.type == "ActorPKField") { return "||to_list" }
                if (this.field_option_selected.type == "ActorField") { return "||to_pk_in_list" }
            }
            if (this.field.type == "ActorPKField") {
                if (this.field_option_selected.type == "ActorListField") { return "||from_list" }
                if (this.field_option_selected.type == "ActorField") { return "||to_pk" }
            }
            if (this.field.type == "RoleListField") {
                if (this.field_option_selected.type == "RoleField") { return "||to_list" }
            }
            if (this.field.type == "RoleField") {
                if (this.field_option_selected.type == "RoleListField") { return "||from_list"}
            }
        },
        is_change_field: function() {
            var is_change_field = false
            this.permission.change_field_options.forEach(option => {
                if (option.text == this.field_selected) { is_change_field = true}
            })
            return is_change_field
        },
        button_variant(model) {
            if (model == this.model_selected) { return "info" } else { return "secondary" }
        },
        validate_selection() {
            if (!this.field_selected && this.field.type != "ObjectField") {
                this.error_message = "This field cannot be set to an object. You must chose a field on an object."
                return false
            }
            return true
        },
        change_dependent_field() {
            if (!this.validate_selection()) { return }
            this.$emit('change-dependent-field', {model_selected: this.model_selected,
                field_selected: this.field_option_selected.text, transform_string: this.get_transform_string(),
                field_is_change_field: this.is_change_field() })
            this.$bvModal.hide(this.modal_id)
        },
        remove_dependent_field() {
            this.$emit('change-dependent-field', {model_selected: null})
            this.$bvModal.hide(this.modal_id)
        }
    }

}

</script>