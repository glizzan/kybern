<template>

    <span>

        <!-- Show response if shortcut used -->
        <action-response-component v-if="shortcut_taken" :response=response></action-response-component>

        <!-- Default display button -->
        <b-button-group v-if="!button_template_provided">
            <b-button id="take_action" :disabled=!has_permission @click="shortcut">{{ verb }}</b-button>
            <b-button id="propose_action"  @click="open_extra">
                <b-icon-caret-up v-if="show_inline_interface"></b-icon-caret-up>
                <b-icon-caret-down v-else></b-icon-caret-down>
            </b-button>
        </b-button-group>
        <b-spinner v-if="shortcut_taken && action_sent && !response" small class="ml-2" label="Spinner"></b-spinner>

        <!-- Otherwise use button or icon provided via default slot -->
        <span @click="open_extra"><slot></slot></span>

        <!-- Display inline -->
        <b-card v-if="inline && show_inline_interface"  bg-variant="light" class="mt-3">
            <action-form-component v-on:take-action="pass_along" :response=response :verb=verb
                :has_permission=has_permission :has_condition=has_condition >
                </action-form-component>
        </b-card>

        <!-- Or view as separate modal -->
        <b-modal v-else :id=modal_id title="Take Action" hide-footer>
            <action-form-component v-on:take-action="pass_along" :response=response :verb=verb
                :has_permission=has_permission :has_condition=has_condition></action-form-component>
        </b-modal>

    </span>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ActionFormComponent from '../actions/ActionFormComponent'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['verb', 'action_name', 'alt_target', 'response', 'check_permissions_params', 'inline'],
    components: { ActionFormComponent, ActionResponseComponent },
    store,
    data: function() {
        return {
            shortcut_taken: false,
            show_inline_interface: false,
            // update check_permissions to return yes/no/conditional, then we can use this
            has_condition: false
        }
    },
    created () {
        var params = {
            name: this.action_backend_name,
            alt_target: this.alt_target ? this.alt_target : null,
            params: this.check_permission_params ? this.check_permission_params : null
        }
        this.checkPermission(params).catch(error => {  this.error_message = error; console.log(error) })
    },
    computed: {
        ...Vuex.mapState({ user_permissions: state => state.permissions.current_user_permissions }),
        modal_id: function() { return this.verb + "_action_modal" },
        button_template_provided () {
            return !!this.$slots.default
        },
        action_backend_name: function() {
            if (this.action_name) { return this.action_name }
            else { return this.verb.replace(/ /g,"_") }   // replaces spaces in user-visible text with udnerscores
        },
        has_permission: function() { return this.user_permissions[this.action_backend_name] },
    },
    methods: {
        ...Vuex.mapActions(['checkPermission']),
        shortcut() {
            this.$emit('take-action')
            this.shortcut_taken = true
            this.action_sent = true
        },
        open_extra() {
            if (this.inline) {
                if (this.show_inline_interface == true )
                    this.show_inline_interface = false
                else {
                    this.show_inline_interface = true
                }
            } else {
                this.$bvModal.show(this.modal_id)
            }
        },
        pass_along(extra_data) {
            this.$emit('take-action', extra_data)
        }
    }

}

</script>

<style scoped>

    #take_action {
        background-color: white;
        color: #17a2b8;
        font-weight: bold;
        border: 1px solid #ced4da;
    }

    #propose_action {
        background-color: #e9ecef;
        border: 1px solid #ced4da;
        color: #495057;
    }



</style>