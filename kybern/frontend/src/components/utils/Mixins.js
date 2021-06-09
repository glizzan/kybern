import Vuex from 'vuex'


var UtilityMixin = {
    methods: {
        shorten_text: function (text, max_length=50) {
            if ((typeof text) === "string" && text.length > max_length) {
                return text.substring(0, max_length) + "..."
            } else {
                return text
            }
        }
    }
}

var ConfiguredFieldsMixin = {
    computed: {
    ...Vuex.mapGetters(['role_to_options', 'user_pk_to_options', 'getUser']),
    },
    methods: {
        change_field(field_info) {
            if (!this.configuration_fields) { console.log("Error! Must set configuration_fields property.")}
            for (let field_index in this.configuration_fields) {
                if (this.configuration_fields[field_index].field_name == field_info.field_name) {
                    this.configuration_fields[field_index].value = field_info.new_value
                }
            }
        },
        process_initial_fields(fields) {
            // Takes in formats of varying kinds, returns a list of fields

            // Restructure fields into list of dicts, if necessary (sometimes fields are passed in as a dict)
            if (!Array.isArray(fields)) {
                fields = Object.values(fields)
            }

            // checks roles and actors and makes sure they're correctly formatted too
            var new_fields = fields.map(field => {
                if (field.type == "RoleListField" && field.value && field.value.length > 0 && !field.value[0].name) {
                    field.value = this.role_to_options(field.value)
                }
                if (field.type == "ActorListField" && field.value && field.value.length > 0  && !field.value[0].name) {
                    field.value = this.user_pk_to_options(field.value)
                }
                return field
            })

            return new_fields
        }
    }
}

var ReplacePKsWithUsernamesMixin = {
    methods: {
        process_description(description, pk) {
            var pks = description.match(/\d+/g)
            if (!pks) { return description }
            pks.forEach(pk => {
                var username = this.getUserName(pk)
                description = description.replace(pk, username)
            })
            return description
        },
        replace_pks_with_usernames(actions) {
            for (let index in actions) {
                var action_item = actions[index]
                if (["AddMembers", "RemoveMembers", "AddGovernor", "RemoveGovernor", "AddOwner", "RemoveOwner",
                        "AddPeopleToRole", "RemovePeopleFromRole"].includes(action_item.change_type)) {
                    action_item.description = this.process_description(action_item.description)
                }
            }
            return actions
          }
    }
}

var PermissionGroupMixin = {
    methods: {
        create_permission_groups(permission_options) {
            var new_options = {}
            for (let index in permission_options) {
                var option = permission_options[index]
                if (option.group in new_options) {
                    new_options[option.group].push(option)
                } else {
                    new_options[option.group] = [option]
                }
            }
            var grouped_options = []
            for (let group in new_options) {
                if (["Leadership", "Community", "Permissions", "Miscellaneous"].indexOf(group) > -1) {
                    grouped_options.push({section: group, permissions: new_options[group]})
                } else {
                    grouped_options.unshift({section: group, permissions: new_options[group]})
                }
            }
            return grouped_options
        }
    }
}

var TargetGroupMixin = {
    data: function() {
        return {
            resources_loaded: false
        }
    },
    created () {
        this.getForums().then(response => {
            this.getLists().then(response => {
                this.getDocuments().then(response => { this.resources_loaded = true })
            })
        })
    },
    computed: {
        ...Vuex.mapState({
            group_name: state => state.group_name,
            group_pk: state => state.group_pk,
            forums: state => state.forums.forums,
            documents: state => state.documents.documents,
            lists: state => state.simplelists.lists
        })
    },
    methods: {
        ...Vuex.mapActions(['getForums', 'getLists', 'getDocuments']),
        create_target_groups() {

            var target_options = []

            target_options.push({
                resource_type: 'Groups',
                items: [
                    { name: this.group_name, pk: this.group_pk, model: 'group' }
                ]
            })

            if (this.forums) {
                target_options.push({
                    resource_type: 'Forums',
                    items: this.forums.map((forum) => { return { name: forum.name, pk: forum.pk, model: 'forum' } })
                })
            }

            if (this.documents) {
                target_options.push({
                    resource_type: 'Documents',
                    items: this.documents.map((doc) => { return { name: doc.name, pk: doc.pk, model: 'document' } })
                })
            }

            if (this.lists) {
                target_options.push({
                    resource_type: 'Lists/Tables',
                    items: this.lists.map((list) => { return { name: list.name, pk: list.pk, model: 'simplelist' } })
                })
            }

            return target_options

        }
    }
}


export { UtilityMixin, ConfiguredFieldsMixin, ReplacePKsWithUsernamesMixin, PermissionGroupMixin, TargetGroupMixin }