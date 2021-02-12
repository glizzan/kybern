<template>

    <span>

        <div v-if="field.type=='CharField'" class="d-inline-block">
            <div class="input-group-prepend">
                <span class="input-group-text" id=field.name>{{ label(field) }}</span>
            </div>
            <input type="text" class="form-control" aria-label=field.name aria-describedby="field.name label"
                v-model=field.value :required=field.required>
        </div>

        <span v-if="field.type=='BooleanField'">
            <b-form-checkbox v-model=field.value name="checkbox-1" value="true" unchecked-value="false">
                {{ label(field) }}
            </b-form-checkbox>
        </span>

        <div v-if="field.type=='IntegerField'" class="d-inline-block">
            <div class="input-group-prepend">
                <span class="input-group-text" id=field.name>{{ label(field) }}</span>
            </div>
            <input type="number" class="form-control" aria-label=field.name aria-describedby="field.name label"
                v-model=field.value
                :required=field.required>
        </div>

        <!-- Should be a choice field populated by current roles -->
        <div v-if="field.type=='RoleField' || field.type=='RoleListField'" class="permissionrolefield">

            <b-input-group :prepend="label(field)">
                <vue-multiselect class="w-50" v-model=field.value :options=rolesAsOptions :allow-empty="true"
                :multiple="select_field_is_multiple(field)" :close-on-select="true" placeholder="Select roles"
                label="name" track-by="name">
                </vue-multiselect>
            </b-input-group>

        </div>

        <!-- Should be a multiselect field populated by current members -->
        <div v-if="field.type=='ActorField' || field.type =='ActorListField'" class="permissionactorfield">

            <b-input-group :prepend="label(field)">
                <vue-multiselect class="w-50"  v-model=field.value :options=groupMembersAsOptions :allow-empty="true"
                    :multiple="select_field_is_multiple(field)" :close-on-select="true" placeholder="Select actors"
                    label="name" track-by="pk">
                </vue-multiselect>
            </b-input-group>

        </div>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import Multiselect from 'vue-multiselect'


export default {

    store,
    components: { "vue-multiselect": Multiselect },
    props: ['initial_field'],
    data: function() {
        return {
            field: null
        }
    },
    created () { this.field = this.initial_field },
    watch: {
        field: function(val) {
            this.$emit('field-value-change', {field_name: this.field.name, new_value: this.field.value})
        }
    },
    computed: {
        ...Vuex.mapGetters(['rolesAsOptions', 'groupMembersAsOptions'])
    },
    methods: {
        select_field_is_multiple(field) {
            if (field.other_data && field.other_data.multiple) {
                return field["other_data"]["multiple"]
            } else {
                return true  // By default, select fields allow multiple
            }
        },
        label(field) {
            if (field.display) { return field.display } else { return field.label }
        }
    }

}

</script>