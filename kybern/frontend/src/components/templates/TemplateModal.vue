<template>

    <b-modal :id="'apply_template_modal_' + scope" :title=title_string size="xl" hide-footer>

        <template-component :scope="new_scope" :target_id="target_id" :target_model="target_model"></template-component>

    </b-modal>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import TemplateComponent from '../templates/TemplateComponent'


export default {

    props: ['scope', 'target_id', 'target_model'],
    components: { TemplateComponent },
    computed: {
        title_string: function() { return "Apply " + this.scope + " templates" },
        new_scope: function() { if (this.scope == "group") { return "community"} else { return this.scope } }
    }

}

</script>