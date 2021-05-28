<template>

    <div>

        <span v-if="!complete">

            <b-form-group>
                <b-form-radio-group id="action-mode-buttons" v-model="mode" :options="options"
                    button-variant="outline-info" name="action-mode-buttons" buttons>
                </b-form-radio-group>
            </b-form-group>

            {{ prompt_text }}

            <b-form-group id="action_note" class="mt-2">
                <b-form-textarea id="text" name="text" v-model="action_note_text" :maxlength="200"
                    placeholder="Write your note here">
                </b-form-textarea>
            </b-form-group>

        </span>

        <div v-if="warning" class="text-danger mb-2">{{ warning }}</div>
        <action-response-component :response=response></action-response-component>

        <b-button v-if="!complete" variant="info" id="submit_action" @click="submit">submit</b-button>
        <b-spinner v-if="action_sent && !response" small label="Spinner" class="ml-2"></b-spinner>

    </div>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ActionResponseComponent from '../actions/ActionResponseComponent'


export default {

    props: ['verb', 'response', 'has_permission', 'has_condition'],
    components: { ActionResponseComponent },
    store,
    data: function() {
        return {
            mode: null,
            warning: null,
            action_note_text: "",
            complete: false,
            action_sent: false
        }
    },
    created () { if (!this.actor_can_take) { this.mode = "propose"} },
    watch: {
        response: function(val) {
            if (val && val.data.action_status && val.data.action_status != "invalid") {
                if (this.action_note_text != "") {
                    this.addNoteToAction({action_pk: val.data.action_pk, note: this.action_note_text})
                }
                this.complete = true
            }
        }
    },
    computed: {
        actor_can_take: function() { return this.has_permission && !this.has_condition },
        note_required: function() { return !this.has_permission },
        options: function() {
            var options = []
            options.push({text: 'Take action ' + this.verb, value: "take", disabled: !this.actor_can_take})
            options.push({text: 'Propose action ' + this.verb, value: "propose", disabled: false})
            return options
        },
        prompt_text: function() {
            if (this.mode == null) {
                return "Please decide if you're taking or proposing an action."
            }
            if (this.mode == "propose") {
                if (this.actor_can_take) {
                    return "When proposing an action, it's helpful to provide some extra context via a note. (Optional, 200 char. max)"
                } else {
                    return "Please explain why you want to take this action. (Required, 200 char. max)"
                }
            }
            if (this.mode == "take") {
                return "It can be helpful to provide extra context as to why you've taken this action. (Optional, 200 char. max)"
            }
            return "error"
        }
    },
    methods: {
        ...Vuex.mapActions(['addNoteToAction']),
        submit() {
            if (!this.mode) {
                this.warning = "You must specify whether you're taking or proposing an action."
                return
            }
            if (this.note_required && this.action_note_text == "") {
                this.warning = "The action note is required."
                return
            }
            this.warning = null
            this.action_sent = true

            if (this.mode == "propose") {
                var proposed = this.actor_can_take ? "propose-vol" : "propose-req"
                this.$emit('take-action', {proposed: proposed})
            } else {
                this.$emit('take-action', {})  // may need more data passed back
            }
        }
    }

}

</script>