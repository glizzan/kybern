<template>

    <div>

        <!-- If conditions have been configured already, displays them plus a button for add another. -->

        <div v-for="(item, key) in conditions_set" v-bind:key=key class="d-block">
            <b-button variant=light class="mb-2 existing-condition" @click="condition_edited=key"> {{ item.name }} </b-button>
            <b-icon-info-circle class="ml-3" v-b-tooltip.hover.html="extra_info(item)"></b-icon-info-circle>
        </div>

        <!-- If no conditions selected, or add_new clicked, displays a box for selecting. -->

        <b-button variant="outline-secondary" class="btn-sm mb-2 d-block add-condition"
            @click="view_selector=true">Add condition</b-button>

        <b-form-select v-if="view_selector" v-model="condition_selected" :options="processed_condition_options"
            :select-size="4" name="condition_select"></b-form-select>

        <!-- If condition selected, displays editor for that condition -->

        <b-modal :id="'configure_condition_' + random_key" :title="'Configure your ' + condition_selected"
            @ok="add_condition_to_set" size="lg">

            <complex-configurable-field-component v-for="field in configuration_fields" :field=field
                v-on:field-changed="change_field" v-bind:key=field.field_name :conditioned_on=conditioned_on>
            </complex-configurable-field-component>

            <span v-if="configuration_fields.length == 0">There are no fields to configure.</span>

            <template #modal-footer="{ ok }">
                <b-button v-if="condition_edited" variant="outline-secondary" class="btn-sm d-block remove-condition"
                    @click="remove_condition">remove</b-button>
                <b-button size="sm" variant="info" class="condition-ok" @click="ok()">OK</b-button>
            </template>

        </b-modal>

    </div>

</template>


<script>

import Vue from 'vue'
import Vuex from 'vuex'
import store from '../../store'
import ComplexConfigurableFieldComponent from '../fields/ComplexConfigurableFieldComponent'
import { ConfiguredFieldsMixin } from '../utils/Mixins'


export default {

    props: ['initial_conditions', 'conditioned_on'],
    components: { ComplexConfigurableFieldComponent },
    mixins: [ConfiguredFieldsMixin],
    store,
    data: function() {
        return {
            random_key: null,
            view_selector: false,
            removed_condition_element_ids: [],
            condition_selected: "",
            configuration_fields: [],
            condition_edited: null,
            conditions_set: {}
        }
    },
    created() {
        this.random_key = Math.random()
        if (this.initial_conditions) { this.set_initial_conditions() }
    },
    watch: {
        initial_conditions: function (val) {
            if (val) { this.set_initial_conditions() }
        },
        condition_selected: function (val) {
            if (val) {
                this.configuration_fields = this.get_configuration_fields();
                this.$bvModal.show("configure_condition_" + this.random_key)
                this.view_selector = false
            }
        },
        condition_edited: function (val) {
            if (val) {
                this.configuration_fields = this.conditions_set[val]["fields"]
                this.$bvModal.show("configure_condition_" + this.random_key)
                this.view_selector = false
            }
        }
    },
    computed: {
        ...Vuex.mapState({
            condition_options: state => state.permissions.condition_options
        }),
        ...Vuex.mapGetters(['getConditionConfigurationFields']),
        processed_condition_options: function() {
            var options = []
            options.push({
                label: "Decision Conditions",
                options: this.condition_options.filter(option => !option.value.includes("Filter"))
            })
            options.push({
                label: "Filter Conditions",
                options: this.condition_options.filter(option => {
                    if (option.value.includes("Filter")) {
                        if (!option.linked) { return true }
                        // get permission type passed in from Permissions Editor
                        // if (this.permission.linked && this.permission.linked.includes(option.value)) {
                        //     return true
                        // }
                    }
                    return false
                })
            })
            return options
        }
    },
    methods: {
        set_initial_conditions() {
            // delete old stuff if it exists
            console.log("Setting initial conditions")
            var keys_to_remove = []
            for (let index in Object.keys(this.conditions_set)) {
                keys_to_remove.push(Object.keys(this.conditions_set)[index])
            }
            keys_to_remove.forEach(old_key => { Vue.delete(this.conditions_set, old_key) })

            // set stuff passed down
            console.log("Cleared conditions set: ", this.conditions_set)
            for (let unique_id in this.initial_conditions.conditions) {
                var initial = this.initial_conditions.conditions[unique_id]
                var key = Math.random()
                var fields = this.process_initial_fields(initial.fields)
                var info = this.process_fields_into_info(initial.fields)
                Vue.set(this.conditions_set, key, {
                    name: initial.display_name, fields: fields, info: info, element_id: initial.element_id,
                    changed: false
                })
            }
        },
        get_configuration_fields() {
            var field_data = []
            if (this.condition_selected) {
                field_data = this.getConditionConfigurationFields(this.condition_selected)
                return Object.values(field_data)
            }
            return []
        },
        process_fields_into_info(fields) {
            if (!Array.isArray(fields)) { fields = Object.values(fields) }
            return fields.map(field => { return { label: field.display, value: field.value } })
        },
        extra_info(item) {
            var info_string = ""
            item.info.forEach(field => {
                if (Array.isArray(field.value)) {
                    field.value = field.value.map(item => { return item.name }).join()
                }
                info_string += field.label + ": " + field.value + "<br /><br />"
            })
            return info_string
        },
        add_condition_to_set() {

            var info = this.process_fields_into_info(this.configuration_fields)

            if (this.condition_edited) {
                this.conditions_set[this.condition_edited]["changed"] = true
                this.conditions_set[this.condition_edited]["fields"] = this.configuration_fields
                this.conditions_set[this.condition_edited]["info"] = info
            } else {
                var key = Math.random()
                Vue.set(this.conditions_set, key, {
                    name: this.condition_selected, fields: this.configuration_fields, info: info, element_id: null
                })
            }

            // clear data
            this.condition_edited = null
            this.configuration_fields = []
            this.condition_selected = ""
        },
        remove_condition() {
            if (this.condition_edited) {
                if(this.conditions_set[this.condition_edited]["element_id"]) {
                    this.removed_condition_element_ids.push(this.conditions_set[this.condition_edited]["element_id"])
                }
                this.$delete(this.conditions_set, this.condition_edited)
                this.condition_edited = null
                this.configuration_fields = []
                this.$bvModal.hide("configure_condition_" + this.random_key)
            }
        }
    },

}

</script>
