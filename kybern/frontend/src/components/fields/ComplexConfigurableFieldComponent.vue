<template>

    <div class="my-3">

        <!-- Can't be dependent field t-->
        <span v-if="!can_be_dependency_field(field)">
            <field-component v-on:field-changed="change_field" :initial_field=field></field-component>
        </span>

        <!-- Can be dependent field but isn't -->
        <span v-if="can_be_dependency_field(field) && !is_dependency_field(field.value)">

            <b-container><b-row>
                <b-col cols="8">
                    <field-component v-on:field-changed="change_field" :initial_field=field></field-component>
                </b-col>
                <b-col>
                    <dependent-field-manager-component v-on:field-changed="change_field" :field=field>
                    </dependent-field-manager-component>
                </b-col>
            </b-row></b-container>

        </span>

        <!-- Is dependent field -->
        <span v-if="can_be_dependency_field(field) && is_dependency_field(field.value)">
            <dependent-field-manager-component v-on:field-changed="change_field" :field=field>
            </dependent-field-manager-component>
        </span>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import FieldComponent from '../fields/FieldComponent'
import DependentFieldManagerComponent from '../fields/DependentFieldManagerComponent'


export default {

    store,
    props: ['field', 'conditioned_on'],
    components: { FieldComponent, DependentFieldManagerComponent },
    methods: {
        can_be_dependency_field(field) {
            if (!this.conditioned_on || this.conditioned_on == "leadership") { return false }
            return field.can_depend
        },
        is_dependency_field(value){
            if (value && typeof(value) == "string") {
                if (value.substring(value.length-2, value.length) == "}}" && value.substring(0,2) == "{{") {
                    return true
                }
            }
            return false
        },
        change_field(emitted_data) { this.$emit('field-changed', emitted_data)}
    }

}

</script>