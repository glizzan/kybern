<template>

    <span>

        <h4 class="mb-3">{{ capitalize(scope) }} Templates</h4>

            <error-component :message=error_message></error-component>

            <span v-if="selected_template">

                <span v-if="create_group || user_permissions.apply_template">

                <template-info-component :template=selected_template :create_group=create_group :display_select=false>
                </template-info-component>

                <div v-if="configuration_fields.length > 0" class="my-4">
                    <h5 class="mt-3 font-weight-bold">Configure fields for template: {{ this.selected_template.name }}.</h5>

                    <field-component v-for="field in configuration_fields" v-on:field-changed="change_field"
                        :initial_field=field v-bind:key=field.field_name></field-component>

                </div>
                <div v-else class="my-4">
                    <b>There are no fields to configure.</b>
                </div>


                <action-response-component :response=apply_template_response></action-response-component>
                <b-button v-if="!create_group" id="submit_apply_template"
                    v-on:click="apply_template(selected_template)" variant="outline-dark" size="sm" class="my-2">
                    Apply template</b-button>
                </span>
                <span v-else>You do not have permisson to apply templates to this {{ scope }}.</span>

            </span>

            <span v-else>
                <b-card-group deck>
                    <template-info-component v-for="template in scope_templates" v-bind:key=template.pk
                        :template=template :create_group=create_group :display_select=true
                        v-on:template-selected="select_template"></template-info-component>
                </b-card-group>
            </span>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'
import FieldComponent from '../fields/FieldComponent'
import TemplateInfoComponent from '../templates/TemplateInfoComponent'
import { ConfiguredFieldsMixin } from '../utils/Mixins'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    store,
    components: { ErrorComponent, FieldComponent, TemplateInfoComponent, ActionResponseComponent },
    mixins: [ConfiguredFieldsMixin],
    props: ['scope', 'create_group', 'target_id', 'target_model'],
    data: function() {
        return {
            selected_template: null,
            browse_templates: false,
            configuration_fields: [],
            error_message : null,
            apply_template_response: null
        }
    },
    created (){
        this.getTemplatesForScope({ scope: this.scope })
        var target_model = null
        var target_id = null
        if (this.target_model) { target_model = this.target_model } else { target_model = "group" }
        if (this.target_id) { target_id = this.target_id } else { target_id = store.state.group_pk }
        var alt_target = target_model + "_" + target_id
        if (!this.create_group) {
            this.checkPermissions({permissions: {"apply_template": {alt_target:alt_target}}})
            .catch(error => {  this.error_message = error; console.log(error) })
        }
    },
    computed: {
        ...Vuex.mapGetters(['scopeTemplates']),
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        scope_templates: function() { return this.scopeTemplates(this.scope) }
    },
    methods: {
        ...Vuex.mapActions(['getTemplatesForScope', 'applyTemplate', 'checkPermissions']),
        capitalize(text) {
            return text[0].toUpperCase() + text.substring(1)
        },
        clearState() {
            this.selected_template = null
            this.configuration_fields = []
            this.fill_configuration_fields = false
            this.browse_templates = false
            this.error_message = ''
        },
        select_template(template) {
            if (template.supplied_fields) {
                this.selected_template = template
                this.configuration_fields = template.supplied_fields
            } else {
                this.selected_template = template
            }
        },
        validate_template() {
            for (let field in this.configuration_fields) {
                if (this.configuration_fields[field]["required"] && !this.configuration_fields[field]["value"]){
                    this.error_message = "Required field " + this.configuration_fields[field]["field_name"] + " needs a value"
                    return false
                }
            }
            return true
        },
        apply_template() {
            if (!this.validate_template()) { return }
            this.applyTemplate({ target_model: this.target_model, target_pk: this.target_id,
                supplied_fields: this.configuration_fields, template_model_pk: this.selected_template.pk })
            .then(response => { this.apply_template_response = response })
        }
    }

}

</script>