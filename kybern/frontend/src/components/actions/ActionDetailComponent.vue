<template>

    <span v-if="ready_to_render">

        <h5>Details for action {{ action.action_pk }}: {{ action.description }}</h5>

        <b-card border-variant="secondary" class="my-3">
                Action {{ action.action_pk }} ({{ action.description }}) was taken by {{ action.actor }}
                on {{ action.display_date }}.
        </b-card>

        <b-card v-if=action.is_template bg-variant="light" header="This is a template action" class="my-3">
                <b-card-text>
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
                </b-card-text>
        </b-card>

        <b-card border-variant="secondary" class="my-3" v-if="action.has_condition" no-body>
            <b-card-title class="bg-light text-center pt-2 m-0 text-muted"><h5>Conditions on Action</h5></b-card-title>
            <b-tabs card>
                <b-tab v-for="condition in ordered_conditions" v-bind:key="condition.pk"
                        :title="condition.type + ' ' + condition.pk">
                    <b-card-text>

                        <component v-bind:is="condition.type" :condition_pk=condition.pk
                            :condition_type=condition.type :action_details=action></component>

                    </b-card-text>
                </b-tab>
            </b-tabs>
        </b-card>

        <b-card border-variant="secondary" class="my-3">
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
            action: null
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
        ...Vuex.mapState({ actions: state => state.concord_actions.actions }),
        ordered_conditions: function() {
            return this.action.has_condition.conditions.slice().sort(function(a,b){
                if (a.pk < b.pk) { return -1 }
                if (a.pk > b.pk) { return 1 }
                return 0
            })
        }
    },
    methods: {
        ...Vuex.mapActions(['addOrUpdateAction']),
    }

}

</script>
