<template>

    <span>

        <span v-if="model_selected">
            <span v-if="field.display">{{ field.display }}</span>
            <span v-if="field.label">{{ field.label }}</span>
            <b-button class="btn-sm btn-info ml-2">
                <small><b>set as: {{model_selected}}<span v-if="field_selected">'s {{field_selected}}</span></b></small>
                <span class="badge badge-info ml-1 edit-dependent-field" v-b-modal="dependent_field_modal_id">🖉</span>
                <span class="badge badge-info ml-1 delete-dependent-field" @click="remove_dependent_field()">🗑</span>
            </b-button>
        </span>

        <span v-else>
            <span class="badge badge-info add-dependent-field" v-b-modal="dependent_field_modal_id">
                add dependency</span>
        </span>

        <dependent-field-component :modal_id=dependent_field_modal_id :field=field :initial_model_selected=model_selected
            :initial_field_selected=field_selected v-on:change-dependent-field=change_dependent_field>
        </dependent-field-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import DependentFieldComponent from '../fields/DependentFieldComponent'


export default {

    components: { DependentFieldComponent },
    store,
    props: ['field'],
    data: function() {
        return {
            model_selected: null,
            field_selected: null
        }
    },
    created () { this.parse_string(this.field.value) },
    watch: { field: function(field) { this.parse_string(field.value) }},
    computed: {
        dependent_field_modal_id: function() {
            var id = "configure_dependent_field_" + Math.random()
            return id.replace(".", "")
        }
    },
    methods: {
        change_dependent_field(emitted_data) {
            this.model_selected = emitted_data.model_selected
            this.field_selected = emitted_data.field_selected
            var new_string = this.reform_string(emitted_data.transform_string, emitted_data.field_is_change_field)
            this.$emit('field-changed', {field_name: this.field.field_name, new_value: new_string})
        },
        parse_string(provided_string) {

            if (!provided_string || typeof(provided_string) != "string") { return }

            // process string into tokens
            var chopped_string = provided_string.substring(2, provided_string.length-2)
            chopped_string = chopped_string.split("||")[0]
            var tokens = chopped_string.split(".")

            // if this isn't a string starting with {{context.}} flag for developer
            if (tokens[0] != "context") { console.log("problem with " + provided_string); return }

            // Select model
            this.model_selected = tokens[1]

            this.field_selected = null
            if (tokens.length >= 3) {
                if (tokens[1] == "action" && tokens[2] == "change") {
                    this.field_selected = tokens[3]
                } else {
                    this.field_selected = tokens[2]
                }
            }
        },
        reform_string(transform_string, field_is_change_field) {
            if (this.model_selected) {
                var base_str = "{{context." + this.model_selected.toLowerCase()
                if (this.field_selected) {
                    if (field_is_change_field) { base_str += ".change"}
                    base_str += "." + this.field_selected
                }
                if (transform_string) {base_str += transform_string}
                base_str += "}}"
                return base_str
            }
            return null
        }
    }

}

</script>