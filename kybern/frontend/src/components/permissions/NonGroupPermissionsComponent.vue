<template>

    <complex-permissions-display-component :permissions=permissions :item_id=item_id :item_model=item_model
        :item_name=item_name>
    </complex-permissions-display-component>

</template>

<script>

import Vuex from 'vuex'
import store from '../../store'
import ComplexPermissionsDisplayComponent from '../permissions/ComplexPermissionsDisplayComponent'


export default {

    components: { ComplexPermissionsDisplayComponent },
    props: ['item_id', 'item_model', 'item_name'],
    store,
    created: function () {
        this.getPermissionsForItem({ item_id: this.item_id, item_model: this.item_model })
            .catch(error => {  this.error_message = error })
    },
    computed: {
        ...Vuex.mapGetters(['permissionsForItem']),
        permissions: function() {
            return this.permissionsForItem(this.item_id + "_" + this.item_model, true)
        },
    },
    methods: {
        ...Vuex.mapActions(['getPermissionsForItem']),
    }

}

</script>