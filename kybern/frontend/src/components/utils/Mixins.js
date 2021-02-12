
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

export { UtilityMixin, ConfiguredFieldsMixin }