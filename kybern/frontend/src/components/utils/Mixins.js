
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
    methods: {
        change_field(field_info) {
            if (!this.configuration_fields) { console.log("Error! Must set configuration_fields property.")}
            for (let field_index in this.configuration_fields) {
                if (this.configuration_fields[field_index].field_name == field_info.field_name) {
                    this.configuration_fields[field_index].value = field_info.new_value
                }
            }
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

export { UtilityMixin, ConfiguredFieldsMixin, ReplacePKsWithUsernamesMixin }