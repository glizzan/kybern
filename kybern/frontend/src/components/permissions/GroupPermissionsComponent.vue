<template>

    <complex-permissions-display-component :permissions=permissions :item_id=group_pk :item_model="'group'"
        :item_name=group_name>
    </complex-permissions-display-component>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ComplexPermissionsDisplayComponent from '../permissions/ComplexPermissionsDisplayComponent'

export default {

    components: { ComplexPermissionsDisplayComponent },
    props: ['group_pk'],
    store,
    created: function () {
        this.getPermissionsForItem({ item_id: this.group_pk, item_model: 'group' })
            .catch(error => {  this.error_message = error })
    },
    computed: {
        ...Vuex.mapGetters(['permissionsForGroup']),
        group_name: function() { return store.state.group_name },
        permissions: function() {
            // get all permissions in group, not just for items
            return this.permissionsForGroup()
        },
    },
    methods: {
        ...Vuex.mapActions(['getPermissionsForItem']),
    }

}

</script>