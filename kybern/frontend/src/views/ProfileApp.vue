<template>

    <span>

        <navbar-component :user_name=user_name :signed_in=signed_in></navbar-component>

        <div class="container">
        <div class="row mt-5">
            <div class="col-12">

                <h3>Profile: {{ user_name }}
                    <b-button v-b-modal.notifications_modal variant="outline-info btn-sm ml-3">notification settings</b-button>
                </h3>

                <b-modal id="notifications_modal" title="Edit your notifications settings" hide-footer>

                    <div class="pb-3">
                        How often should notifications be emailed to you?
                        <b-form-select v-model="email_selected" :options="email_options" class="pt-1"></b-form-select>
                    </div>

                    <b-form-checkbox id="checkbox-everything" v-model="everything" name="checkbox-everything" class="pb-3">
                    Notify me of everything</b-form-checkbox>

                    <b-form-checkbox id="checkbox-creator" v-model="creator" name="checkbox-creator" class="pb-3">
                    Notify me of actions on things I create</b-form-checkbox>

                    <b-form-checkbox id="checkbox-approval" v-model="approval" name="checkbox-approval" class="pb-3">
                    Notify me of actions I may need to approve</b-form-checkbox>

                    <b-form-checkbox id="checkbox-resolved" v-model="resolved" name="checkbox-approval" class="pb-3">
                    Notify me when an action I've taken that had a condition is resolved</b-form-checkbox>

                    <b-button @click="update_settings()">Save changes</b-button>

                    <error-component :message=error_message></error-component>

                </b-modal>

                <div class="row">
                    <div class="col-6">
                        <h4 class="mt-5 mb-3">Groups you're a leader of</h4>
                        <group-list-component v-if="leadership_groups" :groups=leadership_groups></group-list-component>
                        <span v-else><p>You're not a leader of any groups.</p></span>
                    </div>
                    <div class="col-6">
                        <h4 class="mt-5 mb-3">Other groups you're a member of</h4>
                        <group-list-component v-if="other_groups" :groups=other_groups></group-list-component>
                        <span v-else><p>You're not a member of any groups where you're not also a leader.</p></span>
                    </div>
                </div>

                <h4 class="mt-5 mb-2">Notifications</h4>
                <b-table striped hover :fields=fields :items="processed_notifications">
                    <template v-slot:cell(link)="data">
                        <b-button variant="outline-secondary" :href="data.item.link"
                            class="btn-sm action-link-button float-right">link</b-button>
                    </template>
                    <template v-slot:cell(notes)="data">
                        <small>
                        <span v-if="data.item.notes == 'approval'">Your approval may be needed</span>
                        <span v-if="data.item.notes == 'resolved'">An action you took was resolved</span>
                        <span v-if="data.item.notes == 'creator'">Someone took action on something you created</span>
                        </small>
                    </template>
                </b-table>

            </div>

        </div>
        </div>

    </span>

</template>


<script>

let initialState = JSON.parse(window.__INITIAL_STATE__);

import store from '../store'
import axios from '../store/axios_instance'
import NavbarComponent from '../components/utils/NavbarComponent'
import GroupListComponent from '../components/groups/GroupListComponent'
import ErrorComponent from '../components/utils/ErrorComponent'


export default {

    components: { NavbarComponent, GroupListComponent, ErrorComponent },
    store,
    data: function() {
        return {
            error_message: "",
            user_name: initialState.user_name,
            user_pk: initialState.user_pk,
            signed_in: initialState.is_authenticated,
            leadership_groups: initialState.leadership_groups,
            other_groups: initialState.other_groups,
            base_url: initialState.base_url,
            url: initialState.notifications_url,
            initial_notification_settings: initialState.initial_notification_settings,
            notifications: initialState.notifications,
            email_options: [],
            email_selected: null,
            everything: null,
            creator: null,
            approval: null,
            resolved: null,
            fields: [
                { label: "Why", key: "notes", sortable: true },
                { label: "When", key: "created", sortable: true },
                { label: "What", key: "display", sortable: true },
                { label: "Group", key: "group_name", sortable: true },
                { label: "More", key: "link", sortable: false }
            ]
        }
    },
    created () {
        this.email_options = this.initial_notification_settings.email_options
        this.email_selected = this.initial_notification_settings.email_selected
        this.everything = this.initial_notification_settings.everything
        this.creator = this.initial_notification_settings.creator
        this.approval = this.initial_notification_settings.approval
        this.resolved = this.initial_notification_settings.resolved
    },
    computed: {
        processed_notifications: function() {
            var items = []
            this.notifications.forEach(note => {
                var link = this.base_url + "groups/" + note.group_pk + "/#/actions/detail/" + note.action.action_pk
                items.push({notes: note.notes, created: new Date(note.created).toLocaleString(), display: note.action.display,
                            group_name: note.group_name, link: link})
            })
            return items
        }
    },
    methods: {
        update_settings() {
            var params = {email_selected: this.email_selected, everything: this.everything,
                          creator: this.creator, approval: this.approval, resolved: this.resolved}
            axios.post(this.url, params).catch(error => { this.error_message = error.message })
        }
    }

}

</script>

