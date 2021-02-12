<template>

    <span>

        <h4>Advanced Permissions for {{ item_model }} {{ item_id }}</h4>

        <div class="my-3">
            <p>When the governing permission is turned on, any governor can take any action on this item, unless it is an
            action reserved only for owners. Governing permissions are typically turned on by default.</p>

            <span v-if=governing_permission_enabled>The governing permission is <b>turned on</b>.</span>
            <span v-else>The governing permission is <b>turned off</b>.</span>
            <b-button v-if="governing_permission_enabled && user_permissions.disable_governing_permission"
                size="sm" pill variant="outline-secondary" style="font-size: 0.7em;"
                @click="change_permission_override('governing', 'disable')">Turn it off.</b-button>
            <b-button v-if="!governing_permission_enabled && user_permissions.enable_governing_permission"
                size="sm" pill variant="outline-secondary" style="font-size: 0.7em;"
                @click="change_permission_override('governing', 'enable')">Turn it on.</b-button>
        </div>

        <div class="mt-3 mb-2">
            <p>When the foundational permission is turned on, only owners can act on the object.  Any specific permissions
                set below will not apply, and neither will the governing permission.  Foundational permissions are
                typically turned off by default.</p>

            <span v-if=foundational_permission_enabled>The foundational permission is <b>turned on</b>, meaning all
                changes to this object must be approved by the group's owners. The permissions
                set below <span class="text-danger">will not apply</span>.</span>
            <span v-else>The foundational permission is <b>turned off</b>.</span>
            <b-button v-if="foundational_permission_enabled && user_permissions.disable_foundational_permission"
                size="sm" pill variant="outline-secondary" style="font-size: 0.7em;"
                @click="change_permission_override('foundational', 'disable')">Turn it off.</b-button>
            <b-button v-if="!foundational_permission_enabled && user_permissions.enable_foundational_permission"
                size="sm" pill variant="outline-secondary" style="font-size: 0.7em;"
                @click="change_permission_override('foundational', 'enable')">Turn it on.</b-button>
        </div>

        <error-component :message=error_message></error-component>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ErrorComponent from '../utils/ErrorComponent'


export default {

    props: ['item_id', 'item_model', 'item_name'],
    components: { ErrorComponent },
    store,
    data: function() {
        return {
            error_message: ''
        }
    },
    created: function () {
        if (!this.getFoundationalForItem()) {
            this.getPermissionsForItem({ item_id: this.item_id, item_model: this.item_model })
            .catch(error => {  this.error_message = error })
        }
        var alt_target = this.item_model + "_" + this.item_id
        this.checkPermissions({permissions:
            {"enable_governing_permission": {alt_target:alt_target},
            "disable_governing_permission": {alt_target:alt_target},
                "enable_foundational_permission": {alt_target:alt_target},
                "disable_foundational_permission": {alt_target:alt_target}}})
            .catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        ...Vuex.mapGetters(['permissionsForItem',  'getFoundationalForItem',
            'getGoverningForItem']),
        item_key: function() {
            return this.item_id + "_" + this.item_model
        },
        governing_permission_enabled: function() {
            if (this.item_key) { return this.getGoverningForItem(this.item_key) } else { return undefined } },
        foundational_permission_enabled: function() {
            if (this.item_key) { return this.getFoundationalForItem(this.item_key) } else { return undefined } },
    },
    methods: {
        ...Vuex.mapActions(['checkPermissions', 'getPermissionsForItem', 'changePermissionOverride']),
        change_permission_override(governing_or_foundational, enable_or_disable) {
            this.changePermissionOverride({
                item_id : this.item_id, item_model: this.item_model,
                enable_or_disable: enable_or_disable,
                governing_or_foundational: governing_or_foundational })
            .catch(error => {
                this.error_message = error.message
            })
        }
    }

}

</script>