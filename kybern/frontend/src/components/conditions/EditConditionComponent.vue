<template>

    <b-modal :id="modal_id" size="lg" :title="modal_title" hide-footer @hide="wrap_up()">

        <b-button v-if="element_id" @click="remove_condition()" id="delete_condition_button">delete condition</b-button>

        <complex-configurable-field-component v-for="field in configuration_fields" :field=field
            :conditioned_on=conditioned_on v-on:field-changed="change_field" v-bind:key=field.field_name>
        </complex-configurable-field-component>

        <error-component :message=error_message></error-component>

        <!-- Save configuration -->
        <b-button v-if="condition_selected" size="sm" class="mt-3" @click="add_condition()" id="save_condition_button">
                add condition</b-button>
        <b-button v-if="element_id" size="sm" class="mt-3" @click="edit_condition()" id="save_edit_condition_button">
                edit condition</b-button>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import ComplexConfigurableFieldComponent from '../fields/ComplexConfigurableFieldComponent'
import { ConfiguredFieldsMixin } from '../utils/Mixins'

export default {

    components: { ErrorComponent, ComplexConfigurableFieldComponent },
    store,
    mixins: [ConfiguredFieldsMixin],
    props: ['element_id', 'condition_selected'],
    data: function() {
        return {
            configuration_fields: [],
            error_message : ''
        }
    },
    computed: {
        ...Vuex.mapGetters(['getConditionConfigurationFields', 'getPermissionConditionConfigurationFieldsWithData',
                            'getLeadershipConditionConfigurationFieldsWithData']),
        modal_id: function() {
            if (this.element_id) { return "edit_condition_modal_" + this.element_id }
            if (this.condition_selected) { return "edit_condition_modal_new" }
            return undefined
        },
        modal_title: function() {
            if (this.element_id) { return "Configuring " + this.params.condition_type + " (id: " + this.element_id + ")" }
            if (this.condition_selected) { return "Configuring " + this.params.condition_type + " (new)" }
            return undefined
        },
        conditioned_on: function() {
            if ("permission" in this.$parent && this.$parent.permission) { return "permission" }
            else { return "leadership" }
        },
        condition_type: function() {
            if (this.condition_selected) { return this.condition_selected }
            if (this.element_id) { return this.$parent.conditions_with_keys[this.element_id]["type"] }
            return undefined
        },
        params: function() {
            var params ={condition_type: this.condition_type}
            if (this.element_id) { Object.assign(params, {element_id: this.element_id}) }
            if (this.conditioned_on == "permission") {
                Object.assign(params, {permission_or_leadership: "permission", permission_id: this.$parent.permission.pk})
            } else {
                Object.assign(params, {permission_or_leadership: "leadership", leadership_type: this.$parent.leadership_type})
            }
            return params
        }
    },
    created () {
        this.configuration_fields = this.get_configuration_fields();
        if (this.condition_selected) { this.$nextTick(() => { this.$bvModal.show(this.modal_id) }) }
    },
    methods: {
        ...Vuex.mapActions(['addCondition', 'editCondition', 'removeCondition']),
        get_configuration_fields() {
            var field_data = []
            if (this.condition_selected) {
                field_data = this.getConditionConfigurationFields(this.condition_selected)
                return Object.values(field_data)
            }
            if (this.element_id) {
                if (this.$parent.permission) {
                    field_data = this.getPermissionConditionConfigurationFieldsWithData(this.$parent.permission.pk, this.element_id)
                    return Object.values(field_data)
                } else if (this.$parent.leadership_type) {
                    field_data = this.getLeadershipConditionConfigurationFieldsWithData(this.$parent.leadership_type, this.element_id)
                    return Object.values(field_data)
                }
            }
            return []
        },
        wrap_up() {
            this.$emit('finished')
            this.$bvModal.hide(this.modal_id)
        },
        add_condition() {
            var params =this.params
            params["combined_condition_data"] = this.configuration_fields
            this.addCondition(params).then(response => this.wrap_up()).catch(error => this.error_message = error)
        },
        edit_condition() {
            var params =this.params
            params["combined_condition_data"] = this.configuration_fields
            this.editCondition(params).then(response => this.wrap_up()).catch(error => this.error_message = error)
        },
        remove_condition() {
            this.removeCondition(this.params).then(response => this.wrap_up()).catch(error => this.error_message = error)
        }
    }

}

</script>