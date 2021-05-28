<template>

    <span v-if="ready_to_render">

        <b-row align-v="stretch">
            <b-col cols=8>
                <b-card variant="secondary">
                    <h3>Action Details</h3>
                    <div class="info"><span class="label">Action ID</span>: {{ action.action_pk }}</div>
                    <div class="info"><span class="label">Actor</span>: <span class="user-link">{{ action.actor }}</span></div>
                    <div class="info"><span class="label">Time</span>: {{ action.display_date }}</div>
                    <div class="info"><span class="label">Description</span>: {{ action.description }}</div>
                    <div class="info"><span class="label">Status</span>: {{ status }}
                        <span v-if="extra_context" class="extra">{{ extra_context }}</span>
                    </div>
                    <div class="info"><span class="label">Actor's note</span>: {{ action.note }}</div>

                    {{ response }}
                    <b-button v-if="user_is_actor && action.status == 'propose-vol'" variant="outline-secondary"
                        class="my-2" @click="retake_proposed_action">Take your action</b-button>

                    <div v-if=action.is_template>
                        <h6>This is a template action.</h6>
                        <p>When a template action is implemented, it applies a series of other actions.
                            Here are the actions implemented by
                            <span v-if="action.template_description.name">the {{action.template_description.name}}</span>
                            <span v-else>this</span>
                            template:</p>

                        <ul class="my-2">
                            <li v-for="action in action.template_description.actions" v-bind:key=action>{{ action }}</li>
                        </ul>

                            <p>The user has added the following information:</p>
                                <ul class="my-2">
                                    <li v-for="field in action.template_description.supplied_fields.fields" v-bind:key=field>
                                        {{ field }}</li>
                                    <li v-if="action.template_description.supplied_fields.fields.length == 0">
                                            There are no user-supplied fields for this template.</li>
                                </ul>
                            <p>{{action.template_description.foundational}}</p>
                            </div>
                </b-card>
            </b-col>
            <b-col cols=4>
                <b-card variant="secondary">
                    <h5>Conditions on Action</h5>
                        <b-tabs card v-if="action.has_condition.exists">
                            <b-tab v-for="condition in ordered_conditions" v-bind:key="condition.pk"
                                    :title="condition.type + ' ' + condition.pk">
                                <b-card-text>
                                    <component v-bind:is="condition.type" :condition_pk=condition.pk
                                        :condition_type=condition.type :action_details=action></component>
                                </b-card-text>
                            </b-tab>
                        </b-tabs>
                        <span v-else>
                            There are no conditions on this action.
                        </span>
                </b-card>
            </b-col>
        </b-row>

        <b-card variant="secondary" class="my-3">
            <h5>Discussion</h5>
                <CommentListComponent :item_id=action_id :item_model="'action'" class="my-3"> </CommentListComponent>
        </b-card>

    </span>

</template>



<script>

import Vuex from 'vuex'
import store from '../../store'
import CommentListComponent from '../comments/CommentListComponent'
import ApprovalConditionComponent from '../conditions/condition_types/ApprovalConditionComponent'
import ConsensusConditionComponent from '../conditions/condition_types/ConsensusConditionComponent'
import VoteConditionComponent from '../conditions/condition_types/VoteConditionComponent'


export default {

    props: ['action_id'],
    components: { CommentListComponent, "ApprovalCondition": ApprovalConditionComponent,
        "ConsensusCondition": ConsensusConditionComponent, "VoteCondition": VoteConditionComponent  },
    store,
    data: function() {
        return {
            ready_to_render: false,
            action: null,
            response: null
        }
    },
    created () {
        this.action = this.getActionData(this.action_id)
        if (typeof this.action === "undefined") {
            this.addOrUpdateAction({ action_pk: this.action_id })
            .catch(error => { console.log(error) })
        } else {
            this.ready_to_render = true
        }
    },
    watch: {
        actions: function(val) {
            this.action = this.getActionData(this.action_id)
            if (typeof this.action !== "undefined") {
                this.ready_to_render = true
            }
        }
    },
    computed: {
        ...Vuex.mapGetters(['getActionData']),
        ...Vuex.mapState({
            actions: state => state.concord_actions.actions,
            user_pk: state => state.user_pk
        }),
        user_is_actor: function() { return this.action.actor_pk == this.user_pk },
        ordered_conditions: function() {
            return this.action.has_condition.conditions.slice().sort(function(a,b){
                if (a.pk < b.pk) { return -1 }
                if (a.pk > b.pk) { return 1 }
                return 0
            })
        },
        status: function() {
            if (this.action.status.includes("propose")) { return "proposed" }
            else { return this.action.status }
        },
        extra_context: function() {
            if (this.action.status == "propose-vol") {
                return "note: the actor had permission to implement but chose to propose"
            }
            if (this.action.status == "propose-req") {
                return "note: the actor does not have permission to take the action but is proposing it anyway"
            }
            return null
        }
    },
    methods: {
        ...Vuex.mapActions(['addOrUpdateAction', 'retakeAction']),
        retake_proposed_action() {
            this.retakeAction({action_pk: this.action_id})
                .then(response => {
                    this.action = this.getActionData(this.action_id)
                    this.response = response
                })
        }
    }

}

</script>

<style scoped>
    .info { display: block; }
    .label { font-weight: bold; }
    .user-link {
        color: #17a2b8;
        font-weight: bold;
    }
    .extra {
        display: block;
        color: #6c757d;
        font-weight: bold;
    }
</style>