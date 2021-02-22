<template>

    <div :id="unique_identifier" :class="styleclass">
        <span v-if="dismissable && message" class="error-message">
            <b-alert variant="danger" dismissible class="my-2 error-alert"
                :show="show_dismissible_alert" @dismissed="show_dismissible_alert=false" >
                {{ message }}</b-alert>
        </span>
        <span v-else class="error-message">
            {{ message }}
        </span>
    </div>

</template>

<script>

module.exports = {

    props: ['message', 'dismissable'],
    data: function() {
        return {
            unique_identifier: null,
            styleclass: "text-danger",
            show_dismissible_alert: true
        }
    },
    created () {
        this.unique_identifier = Math.random().toString()
        this.render_html()
    },
    watch: {
        message: function() {
            this.render_html();
            this.show_dismissible_alert = true
        }
    },
    methods: {
        render_html() {
            if (this.message && this.message.indexOf("href") !== -1 ) {
                var tag_id = document.getElementById(this.unique_identifier)
                if (tag_id) {
                    tag_id.innerHTML = this.message
                    this.styleclass = "text-secondary"
                }
            }
        }
    }

}

</script>