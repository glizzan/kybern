<template>

    <div class="mb-2">

        <div v-if="field.type == 'CharField' || field.type =='PermissionedModelField'">

            <b-input-group :prepend="label(field)" class="mb-2 mr-sm-2 mb-sm-0">
                <b-form-input :id=field.field_name :name=field.field_name :aria-label=field.field_name
                    :aria-describedby="field.field_name + '_label'" v-model=field.value :required=field.required>
                </b-form-input>
            </b-input-group>

        </div>

        <span v-if="field.type=='BooleanField'">

            <b-form-checkbox v-model=field.value :name=field.field_name value="true" unchecked-value="false"
                class="ml-3" variant="info" switch>{{ label(field) }}</b-form-checkbox>

        </span>

        <div v-if="field.type=='IntegerField'" >

            <b-input-group :prepend="label(field)" class="mb-2 mr-sm-2 mb-sm-0">
                <b-form-input type="number" :id=field.field_name :name=field.field_name :aria-label=field.field_name
                    :aria-describedby="field.field_name + '_label'" v-model=field.value :required=field.required>
                </b-form-input>
            </b-input-group>

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

    </div>

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